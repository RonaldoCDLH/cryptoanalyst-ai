"""Datos ficticios para revisar el diseño sin credenciales ni conexión externa.

Los datos no representan precios, movimientos ni noticias del mercado real.
"""
from __future__ import annotations

from datetime import datetime, timedelta
import math
import random
import pandas as pd

COINS = {
    "BTC": {"name": "Bitcoin", "price": 72840.50, "change": 2.84, "market_cap": 1432.2, "volume": 34.8, "color": "#F59E0B", "seed": 11},
    "ETH": {"name": "Ethereum", "price": 3824.10, "change": 1.36, "market_cap": 459.4, "volume": 18.5, "color": "#9B8AFB", "seed": 19},
    "SOL": {"name": "Solana", "price": 172.80, "change": 5.42, "market_cap": 76.5, "volume": 4.2, "color": "#2DD4BF", "seed": 23},
    "BNB": {"name": "BNB", "price": 604.36, "change": -0.82, "market_cap": 87.9, "volume": 1.9, "color": "#FACC15", "seed": 31},
    "XRP": {"name": "XRP", "price": 0.84, "change": -1.18, "market_cap": 46.7, "volume": 2.1, "color": "#60A5FA", "seed": 47},
    "ADA": {"name": "Cardano", "price": 0.69, "change": 3.12, "market_cap": 24.3, "volume": 0.8, "color": "#F472B6", "seed": 59},
}

DEMO_NEWS = [
    {"tag": "MERCADO", "title": "Ejemplo: operadores observan la volatilidad de Bitcoin", "description": "Titular ficticio usado exclusivamente para mostrar la distribución visual del módulo de noticias.", "time": "Hace 15 min", "tone": "neutral"},
    {"tag": "TECNOLOGÍA", "title": "Ejemplo: aplicaciones del ecosistema Ethereum", "description": "Contenido de muestra. Las noticias verificadas se integrarán después con una fuente autorizada.", "time": "Hace 1 h", "tone": "positive"},
    {"tag": "REGULACIÓN", "title": "Ejemplo: evolución de las normas para activos digitales", "description": "Esta tarjeta no afirma ningún cambio normativo ni corresponde a una noticia publicada.", "time": "Hace 3 h", "tone": "neutral"},
]


def price_history(symbol: str, days: int = 30) -> pd.DataFrame:
    """Serie sintética reproducible. No se descarga información del mercado."""
    coin = COINS[symbol]
    rng = random.Random(coin["seed"] + days)
    base = coin["price"]
    values = []
    for idx in range(days + 1):
        trend = (idx / days - 0.5) * coin["change"] / 95
        wave = math.sin(idx / 4.2 + coin["seed"]) * 0.042
        noise = rng.uniform(-0.016, 0.016)
        values.append(max(0.01, base * (1 + trend + wave + noise)))
    # Consistencia: el último punto coincide con el valor de la tarjeta demo.
    values[-1] = base
    start = datetime(2026, 10, 1) - timedelta(days=days)
    return pd.DataFrame({
        "Fecha": [start + timedelta(days=i) for i in range(days + 1)],
        "Precio": values,
    })


def answer_demo(question: str, selected_symbol: str) -> str:
    """Respuestas por reglas: este módulo NO es todavía un agente con IA."""
    q = question.casefold()
    mentioned = [symbol for symbol, coin in COINS.items() if symbol.casefold() in q or coin["name"].casefold() in q]
    symbol = mentioned[0] if mentioned else selected_symbol
    coin = COINS[symbol]
    if any(token in q for token in ("noticia", "news", "actualidad")):
        return "En esta versión las noticias son **ficticias** y únicamente sirven para probar el diseño. En la siguiente etapa conectaremos NewsAPI o una alternativa adecuada para publicar la aplicación."
    if any(token in q for token in ("compar", "diferencia", "frente a", "versus", " vs ")):
        other = mentioned[1] if len(mentioned) > 1 else ("ETH" if symbol != "ETH" else "BTC")
        c2 = COINS[other]
        return (f"**Comparación ilustrativa ({symbol} / {other}):**\n\n"
                f"- {coin['name']}: **US$ {coin['price']:,.2f}** (variación ficticia {coin['change']:+.2f} %).\n"
                f"- {c2['name']}: **US$ {c2['price']:,.2f}** (variación ficticia {c2['change']:+.2f} %).\n\n"
                "Estos valores son simulados. No son precios actuales ni recomendaciones de inversión.")
    if any(token in q for token in ("precio", "cotiza", "vale", "valor", "mercado", "bitcoin", "ethereum", "solana")):
        return (f"En la **demostración**, {coin['name']} ({symbol}) figura con un precio **ficticio** de "
                f"**US$ {coin['price']:,.2f}** y una variación también ficticia de **{coin['change']:+.2f} %**.\n\n"
                "Cuando conectemos la API de mercado, aquí se mostrarán datos reales con fecha, hora y fuente.")
    return ("Soy el **asistente de demostración** de CryptoAnalyst AI. Aún no utilizo un modelo de IA ni LangGraph: "
            "respondo con reglas sencillas para probar el chat. Puedes preguntarme por el precio ilustrativo de Bitcoin, "
            "comparar Bitcoin con Ethereum o consultar cómo se mostrarán las noticias.\n\n"
            "En la siguiente etapa incorporaremos un agente real con herramientas y memoria.")
