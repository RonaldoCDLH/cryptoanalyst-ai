"""Registro y autenticacion para CryptoAnalyst AI Pro.

Supabase Auth si se configura; SQLite local para el prototipo sin servicios externos.
Las credenciales nunca se almacenan en texto plano.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
import re
import secrets
import sqlite3
from typing import Any

import requests

EMAIL_PATTERN = re.compile(r"^[^@\s]{1,100}@[^@\s]{1,150}\.[^@\s]{2,}$")
ITERATIONS = 390_000


class AuthError(Exception):
    """Mensaje seguro destinado a la interfaz de usuario."""


def _setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""


def provider() -> str:
    url, key = _setting("SUPABASE_URL"), _setting("SUPABASE_ANON_KEY")
    if bool(url) != bool(key):
        raise AuthError("Configuración de registro incompleta: faltan parámetros de Supabase.")
    return "supabase" if url and key else "sqlite_demo"


def durable_accounts() -> bool:
    return provider() == "supabase"


def _db_path() -> Path:
    return Path(os.getenv("CRYPTO_AUTH_DB", "data/crypto_users.sqlite3"))


def _connection() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            salt BLOB NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def _email(raw: str) -> str:
    email = raw.strip().lower()
    if not EMAIL_PATTERN.fullmatch(email) or len(email) > 254:
        raise AuthError("Introduce un correo electrónico válido.")
    return email


def _password(raw: str) -> None:
    if len(raw) < 12 or len(raw) > 128:
        raise AuthError("La contraseña debe tener entre 12 y 128 caracteres.")
    if not any(char.isalpha() for char in raw) or not any(char.isdigit() for char in raw):
        raise AuthError("La contraseña debe incluir letras y números.")


def _supabase_request(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = _setting("SUPABASE_URL").rstrip("/")
    key = _setting("SUPABASE_ANON_KEY")
    try:
        result = requests.post(
            f"{url}/auth/v1/{path}",
            headers={"apikey": key, "Content-Type": "application/json"},
            json=payload,
            timeout=15,
        )
    except requests.RequestException as exc:
        raise AuthError("El servicio de cuentas no está disponible en este momento.") from exc
    if result.status_code >= 400:
        try:
            code = result.json().get("error_code", "")
        except ValueError:
            code = ""
        if code == "email_not_confirmed":
            raise AuthError("Debes confirmar tu correo antes de iniciar sesión.")
        if result.status_code == 429:
            raise AuthError("Demasiados intentos. Inténtalo más tarde.")
        if path.startswith("signup"):
            raise AuthError("No se pudo registrar la cuenta. Verifica el correo o utiliza otro.")
        raise AuthError("Correo o contraseña incorrectos, o cuenta no confirmada.")
    try:
        return result.json()
    except ValueError as exc:
        raise AuthError("El servicio de cuentas no devolvió una respuesta válida.") from exc


def register(full_name: str, email: str, password: str) -> dict[str, Any]:
    name = full_name.strip()
    if not 2 <= len(name) <= 70:
        raise AuthError("Introduce tu nombre (entre 2 y 70 caracteres).")
    email = _email(email)
    _password(password)
    if provider() == "supabase":
        result = _supabase_request(
            "signup",
            {"email": email, "password": password, "data": {"display_name": name}},
        )
        # Con confirmación por correo habilitada Supabase puede no entregar token.
        if not result.get("access_token"):
            return {"confirmation_required": True, "email": email}
        user = result.get("user") or {}
        return {
            "id": str(user.get("id", "")),
            "name": name,
            "email": email,
            "provider": "supabase",
            "token": result["access_token"],
        }

    salt = secrets.token_bytes(24)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    with _connection() as conn:
        try:
            cursor = conn.execute(
                "INSERT INTO users (full_name, email, salt, password_hash) VALUES (?, ?, ?, ?)",
                (name, email, salt, digest),
            )
        except sqlite3.IntegrityError as exc:
            raise AuthError("Este correo ya tiene una cuenta. Inicia sesión.") from exc
    return {"id": str(cursor.lastrowid), "name": name, "email": email, "provider": "sqlite_demo"}


def sign_in(email: str, password: str) -> dict[str, Any]:
    email = _email(email)
    if provider() == "supabase":
        response = _supabase_request(
            "token?grant_type=password", {"email": email, "password": password}
        )
        user = response.get("user") or {}
        token = response.get("access_token")
        if not token:
            raise AuthError("No se pudo iniciar sesión. Confirma tu correo.")
        return {
            "id": str(user.get("id", "")),
            "name": str((user.get("user_metadata") or {}).get("display_name") or email.split("@")[0]),
            "email": email,
            "provider": "supabase",
            "token": token,
        }

    with _connection() as conn:
        row = conn.execute(
            "SELECT id, full_name, salt, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    if row is None:
        # Calculo constante incluso si no existe el usuario.
        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), b"\0" * 24, ITERATIONS)
        raise AuthError("Correo o contraseña incorrectos.")
    uid, name, salt, expected = row
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    if not hmac.compare_digest(actual, expected):
        raise AuthError("Correo o contraseña incorrectos.")
    return {"id": str(uid), "name": name, "email": email, "provider": "sqlite_demo"}


def verify_remote_session(user: dict[str, Any]) -> bool:
    """Comprobar token remoto antes de exponer el panel privado."""
    if user.get("provider") != "supabase":
        return True
    token = user.get("token", "")
    if not token:
        return False
    try:
        response = requests.get(
            _setting("SUPABASE_URL").rstrip("/") + "/auth/v1/user",
            headers={
                "apikey": _setting("SUPABASE_ANON_KEY"),
                "Authorization": "Bearer " + token,
            },
            timeout=8,
        )
        return response.ok and response.json().get("id") == user.get("id")
    except (requests.RequestException, ValueError):
        return False
