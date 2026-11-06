"""Consulta de mercado a CoinGecko; nunca fabrica precios como si fueran reales."""
from __future__ import annotations

from datetime import datetime, timezone
import math
import requests
import pandas as pd

SYMBOL_TO_ID = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
    "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
}
BASE_URL = "https://api.coingecko.com/api/v3"


class MarketAPIError(RuntimeError):
    """La fuente de datos en vivo no respondió con datos utilizables."""


def _json_get(path: str, params: dict, api_key: str = ""):
    headers = {"accept": "application/json", "user-agent": "CryptoAnalystAI-Academic/1.0"}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    try:
        response = requests.get(f"{BASE_URL}{path}", params=params, headers=headers, timeout=12)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketAPIError("No fue posible consultar CoinGecko en este momento.") from exc


def _number(value, *, positive: bool = False) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise MarketAPIError("La API devolvió una cifra inválida.") from exc
    if not math.isfinite(x) or (positive and x <= 0):
        raise MarketAPIError("La API devolvió una cifra fuera de rango.")
    return x


def get_markets(api_key: str = "") -> dict[str, dict]:
    """Devuelve seis activos validados, con precio y cambio de las últimas 24 h."""
    payload = _json_get(
        "/coins/markets",
        {"vs_currency": "usd", "ids": ",".join(SYMBOL_TO_ID.values()),
         "order": "market_cap_desc", "per_page": 20, "page": 1,
         "sparkline": "false", "price_change_percentage": "24h"},
        api_key,
    )
    if not isinstance(payload, list):
        raise MarketAPIError("Formato de mercado inesperado.")
    by_id = {item.get("id"): item for item in payload if isinstance(item, dict)}
    result = {}
    for symbol, coin_id in SYMBOL_TO_ID.items():
        item = by_id.get(coin_id)
        if not item:
            raise MarketAPIError(f"No se recibió el activo {symbol}.")
        change = item.get("price_change_percentage_24h_in_currency")
        if change is None:
            change = item.get("price_change_percentage_24h")
        result[symbol] = {
            "price": _number(item.get("current_price"), positive=True),
            "change": _number(change) if change is not None else 0.0,
            "market_cap": _number(item.get("market_cap") or 0) / 1e9,
            "volume": _number(item.get("total_volume") or 0) / 1e9,
            "updated_at": item.get("last_updated") or datetime.now(timezone.utc).isoformat(),
        }
    return result


def get_history(symbol: str, days: int = 30, api_key: str = "") -> pd.DataFrame:
    """Histórico real en USD; si falla, NO lo sustituye por cifras sintéticas."""
    if symbol not in SYMBOL_TO_ID or days not in (7, 30, 90):
        raise ValueError("Activo o período no admitido.")
    payload = _json_get(
        f"/coins/{SYMBOL_TO_ID[symbol]}/market_chart",
        {"vs_currency": "usd", "days": days}, api_key,
    )
    if not isinstance(payload, dict) or not isinstance(payload.get("prices"), list):
        raise MarketAPIError("Histórico no disponible.")
    points = []
    for item in payload["prices"]:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        try:
            timestamp = _number(item[0])
            price = _number(item[1], positive=True)
            dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        except (MarketAPIError, ValueError, OverflowError):
            continue
        points.append((dt, price))
    if len(points) < 2:
        raise MarketAPIError("No hay suficientes puntos históricos verificables.")
    return pd.DataFrame(sorted(points, key=lambda x: x[0]), columns=["Fecha", "Precio"])


def answer_market(question: str, selected_symbol: str, coins: dict[str, dict]) -> str:
    """Asistente de consulta por reglas con cifras reales, NO un modelo de IA."""
    q = question.casefold()
    mentioned = [s for s, c in coins.items() if c["name"].casefold() in q or
                 any(word == s.casefold() for word in q.replace("/", " ").replace(",", " ").split())]
    primary = mentioned[0] if mentioned else selected_symbol
    coin = coins[primary]
    if any(token in q for token in ("noticias", "noticia", "news", "titular")):
        return ("Las noticias aún no están conectadas a una fuente autorizada para una aplicación pública. "
                "No voy a inventar titulares ni presentar noticias simuladas como actuales.")
    if any(token in q for token in ("compar", "diferencia", "versus", " vs ", "frente a")):
        secondary = mentioned[1] if len(mentioned) > 1 else ("ETH" if primary != "ETH" else "BTC")
        other = coins[secondary]
        return (f"**Comparación de mercado · CoinGecko**\n\n"
                f"- **{coin['name']} ({primary}):** US$ {coin['price']:,.2f} | 24 h: {coin['change']:+.2f} %.\n"
                f"- **{other['name']} ({secondary}):** US$ {other['price']:,.2f} | 24 h: {other['change']:+.2f} %.\n\n"
                "Son cotizaciones consultadas a una API, no predicciones ni consejos de inversión. "
                "Este chat utiliza reglas; todavía no ejecuta un modelo de lenguaje.")
    return (f"**{coin['name']} ({primary})**\n\n"
            f"- **Precio de referencia:** US$ {coin['price']:,.2f}\n"
            f"- **Variación en 24 horas:** {coin['change']:+.2f} %\n"
            f"- **Capitalización:** US$ {coin['market_cap']:,.2f} mil millones\n\n"
            "Fuente: CoinGecko (consulta con caché). El precio puede haber cambiado. "
            "Esta respuesta es informativa y está generada mediante reglas, no por un agente de IA.")
