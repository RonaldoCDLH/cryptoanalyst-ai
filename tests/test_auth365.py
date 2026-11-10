"""Pruebas del registro local y del bloqueo del panel."""
from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import auth365


class TestAccountRegistration(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        overrides = patch.dict(
            os.environ,
            {
                "CRYPTO_AUTH_DB": str(Path(self.workspace.name) / "users.sqlite3"),
                "SUPABASE_URL": "",
                "SUPABASE_ANON_KEY": "",
            },
        )
        overrides.start()
        self.addCleanup(overrides.stop)

    def test_user_registers_and_logs_in(self):
        created = auth365.register("María López", "Maria@Example.com", "strongPassword2026")
        self.assertEqual(created["email"], "maria@example.com")
        self.assertEqual(created["provider"], "sqlite_demo")
        logged = auth365.sign_in("MARIA@EXAMPLE.COM", "strongPassword2026")
        self.assertEqual(logged["id"], created["id"])
        self.assertEqual(logged["name"], "María López")
        self.assertNotIn("token", logged)

    def test_password_is_hashed_and_salted(self):
        auth365.register("Test User", "hash@example.com", "strongPassword2026")
        with sqlite3.connect(os.environ["CRYPTO_AUTH_DB"]) as conn:
            salt, digest = conn.execute("SELECT salt, password_hash FROM users").fetchone()
        self.assertEqual(len(salt), 24)
        self.assertEqual(len(digest), 32)
        self.assertNotIn(b"strongPassword2026", digest)

    def test_duplicate_email_rejected(self):
        auth365.register("Test User", "same@example.com", "strongPassword2026")
        with self.assertRaises(auth365.AuthError):
            auth365.register("Other User", "SAME@example.com", "AnotherPassword2026")

    def test_wrong_password_rejected(self):
        auth365.register("Test User", "wrong@example.com", "strongPassword2026")
        with self.assertRaises(auth365.AuthError):
            auth365.sign_in("wrong@example.com", "incorrectPassword2026")

    def test_unknown_user_rejected(self):
        with self.assertRaises(auth365.AuthError):
            auth365.sign_in("missing@example.com", "incorrectPassword2026")

    def test_password_rules(self):
        for password in ("123456", "alllettersandnone", "123456789012"):
            with self.subTest(password=password):
                with self.assertRaises(auth365.AuthError):
                    auth365.register("Test User", "rules@example.com", password)

    def test_registration_validates_email(self):
        with self.assertRaises(auth365.AuthError):
            auth365.register("Test User", "invalid-email", "strongPassword2026")

    def test_session_is_not_marked_as_permanent(self):
        self.assertFalse(auth365.durable_accounts())


class TestPrivacyGate(unittest.TestCase):
    def test_access_gate_is_before_market_fetch(self):
        source = Path("app.py").read_text(encoding="utf-8")
        self.assertLess(
            source.index("\nrequire_account()\n"),
            source.index("\nMARKET_KEY = get_coingecko_key()"),
        )
        self.assertIn("st.stop()", source)
        self.assertIn("st.session_state.clear()", source)


if __name__ == "__main__":
    unittest.main()
