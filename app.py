"""CryptoAnalyst AI — prototipo visual en Streamlit (modo demostración)."""
from __future__ import annotations

from pathlib import Path
import html
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import COINS, DEMO_NEWS, answer_demo, price_history
from services.market_data import MarketAPIError, get_markets, get_history, answer_market

st.set_page_config(
    page_title="CryptoAnalyst AI | Terminal inteligente",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner=False)
def cached_markets(api_key: str):
    return get_markets(api_key)


@st.cache_data(ttl=900, show_spinner=False)
def cached_history(symbol: str, days: int, api_key: str):
    return get_history(symbol, days, api_key)


def get_coingecko_key() -> str:
    """Opcional: clave demo de CoinGecko en secretos de Streamlit."""
    key = os.environ.get("COINGECKO_DEMO_API_KEY", "")
    if key:
        return key
    try:
        return str(st.secrets["COINGECKO_DEMO_API_KEY"])
    except Exception:
        return ""


MARKET_KEY = get_coingecko_key()
MARKET_LIVE = False
MARKET_ERROR = ""
try:
    snapshot = cached_markets(MARKET_KEY)
    COINS = {sym: {**info, **snapshot[sym]} for sym, info in COINS.items()}
    MARKET_LIVE = True
except MarketAPIError as exc:
    MARKET_ERROR = str(exc)


def historical_series(symbol: str, days: int):
    if MARKET_LIVE:
        try:
            return cached_history(symbol, days, MARKET_KEY)
        except MarketAPIError:
            return None
    return price_history(symbol, days)


if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["BTC", "ETH", "SOL"]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": (
            "Bienvenido a **CryptoAnalyst AI**. Puedes consultar cotizaciones públicas de CoinGecko; "
            "el chat utiliza reglas y todavía no es un modelo de IA." if MARKET_LIVE else
            "Bienvenido a **CryptoAnalyst AI**. Esta sesión muestra datos simulados porque "
            "la API de mercado no está disponible. El chat utiliza reglas, no un modelo de IA."
        )}
    ]


def safe(s: str) -> str:
    return html.escape(str(s))


def heading(eyebrow: str, title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="section-heading"><div class="eyebrow">{safe(eyebrow)}</div>'
        f'<h2>{safe(title)}</h2><p>{safe(subtitle)}</p></div>', unsafe_allow_html=True
    )


def metric_card(label: str, value: str, delta: str, positive: bool = True, symbol: str = "") -> str:
    klass = "up" if positive else "down"
    tag = f'<span class="token-tag">{safe(symbol)}</span>' if symbol else ""
    return (
        f'<div class="metric-card"><div class="metric-top"><span>{safe(label)}</span>{tag}</div>'
        f'<div class="metric-value">{safe(value)}</div>'
        f'<div class="metric-bottom"><span class="{klass}">{safe(delta)}</span>'
        f'<span> · {"CoinGecko" if MARKET_LIVE else "ilustrativo"}</span></div></div>'
    )


def chart_for(symbol: str, days: int, height: int = 365) -> go.Figure:
    history = historical_series(symbol, days)
    if history is None:
        return None
    color = COINS[symbol]["color"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history["Fecha"], y=history["Precio"],
        name=symbol, mode="lines",
        line={"color": color, "width": 3.5, "shape": "spline"},
        fill="tozeroy", fillcolor="rgba(45,212,191,0.035)",
        hovertemplate="%{x|%d %b %Y}<br><b>US$ %{y:,.2f}</b> " + ("(CoinGecko)" if MARKET_LIVE else "(simulado)") + "<extra></extra>",
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=10, t=18, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#96A7BD", family="Arial, sans-serif", size=12),
        xaxis=dict(showgrid=False, zeroline=False, showline=False, tickfont=dict(color="#7890A9")),
        yaxis=dict(showgrid=True, gridcolor="rgba(126,157,189,0.12)",
                   zeroline=False, showline=False, tickprefix="$", tickformat=",.2f", fixedrange=False),
        showlegend=False, hovermode="x unified", dragmode="pan",
    )
    return fig


with st.sidebar:
    st.markdown('<div class="logo"><span class="logo-symbol">◈</span><div>CRYPTO<span>ANALYST</span><small>INTELLIGENCE TERMINAL</small></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-caption">ESPACIO DE TRABAJO</div>', unsafe_allow_html=True)
    section = st.radio(
        "Navegación",
        ["◫  Panel principal", "◈  Explorar mercado", "▤  Noticias", "✦  Asistente IA", "⌘  Arquitectura"],
        label_visibility="collapsed",
    )
    st.markdown('<div class="sidebar-caption">CONFIGURACIÓN</div>', unsafe_allow_html=True)
    selected = st.selectbox("Criptomoneda principal", options=list(COINS), format_func=lambda s: f"{COINS[s]['name']} ({s})")
    sidebar_mode = "Datos públicos verificados" if MARKET_LIVE else "Modo demostración"
    sidebar_note = "CoinGecko · caché de 5 min" if MARKET_LIVE else "API no disponible · datos ficticios"
    st.markdown(
        f'<div class="sidebar-info"><div class="dot"></div><div><strong>{sidebar_mode}</strong>'
        f'<br><span>{sidebar_note}</span></div></div>', unsafe_allow_html=True
    )
    st.markdown('<div class="sidebar-footer">v0.2 · Datos públicos y demo<br>Construido con Python + Streamlit</div>', unsafe_allow_html=True)


st.markdown(
    '<div class="top-line"><span class="crumb">PRODUCTO / CRYPTOANALYST AI</span>'
    f'<span class="demo-pill">● {"MERCADO REAL · COINGECKO" if MARKET_LIVE else "MODO DEMO · DATOS SIMULADOS"}</span></div>', unsafe_allow_html=True
)

if "Panel principal" in section:
    st.markdown(
        '<div class="hero"><div class="hero-badge">◈ INTELIGENCIA DE MERCADO</div>'
        '<h1>El mercado, con una <span>nueva perspectiva.</span></h1>'
        '<p>Explora activos digitales, visualiza tendencias y conversa con un asistente. '
        'Una experiencia diseñada para hacer comprensible la información compleja.</p>'
        '<div class="hero-footer"><span>● DEMOSTRACIÓN INTERACTIVA</span><span>PYTHON · ANALÍTICA · AGENTES IA</span></div>'
        '</div>', unsafe_allow_html=True
    )
    heading("01 / PANORAMA", "Vista general del mercado",
            "Cotizaciones consultadas a CoinGecko; pueden tener retraso." if MARKET_LIVE
            else "Cifras ficticias para validar el diseño; API no disponible.")
    if not MARKET_LIVE:
        st.warning("No se obtuvieron cotizaciones verificables. Se muestra el modo de demostración, sin valores reales.")
    cols = st.columns(4, gap="medium")
    for idx, sym in enumerate(["BTC", "ETH", "SOL", "BNB"]):
        c = COINS[sym]
        with cols[idx]:
            st.markdown(metric_card(c["name"], f"US$ {c['price']:,.2f}", f"{c['change']:+.2f}%", c["change"] >= 0, sym), unsafe_allow_html=True)

    left, right = st.columns([1.84, 1], gap="large")
    with left:
        st.markdown('<div class="panel-heading"><div><span class="eyebrow">GRÁFICA EXPLORATORIA</span><h3>Evolución del precio</h3></div>' + f'<span class="panel-badge">{"HISTÓRICO COINGECKO" if MARKET_LIVE else "SERIE SINTÉTICA"}</span></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f'<div class="selected-coin">{safe(COINS[selected]["name"])} <span>{safe(selected)}</span></div>', unsafe_allow_html=True)
        with c2:
            period = st.radio("Intervalo", ["7D", "30D", "90D"], index=1, horizontal=True, label_visibility="collapsed")
        fig_price = chart_for(selected, int(period[:-1]))
        if fig_price is None:
            st.warning("El histórico de precios no está disponible en este momento. No mostraremos una gráfica inventada.")
        else:
            st.plotly_chart(fig_price, use_container_width=True, config={"displayModeBar": False})
        st.caption("Fuente: CoinGecko; consulta almacenada temporalmente." if MARKET_LIVE
                   else "Visualización sintética; los valores no describen el mercado actual.")
    with right:
        st.markdown('<div class="panel-heading"><div><span class="eyebrow">SEGUIMIENTO</span><h3>Tu lista de observación</h3></div></div>', unsafe_allow_html=True)
        for sym in st.session_state.watchlist:
            c = COINS[sym]
            st.markdown(
                f'<div class="watch-row"><div class="coin-symbol" style="color:{c["color"]}">◈</div>'
                f'<div class="watch-name"><b>{safe(c["name"])}</b><small>{safe(sym)}</small></div>'
                f'<div class="watch-price"><strong>${c["price"]:,.2f}</strong><small class="{"up" if c["change"] >= 0 else "down"}">{c["change"]:+.2f}%</small></div></div>',
                unsafe_allow_html=True,
            )
        options = [sym for sym in COINS if sym not in st.session_state.watchlist]
        if options:
            new_symbol = st.selectbox("Agregar activo", options, key="new_coin", format_func=lambda s: COINS[s]["name"])
            if st.button("+ Añadir a seguimiento", use_container_width=True):
                st.session_state.watchlist.append(new_symbol)
                st.rerun()
        else:
            st.caption("Ya sigues todos los activos de la demostración.")
        if st.session_state.watchlist and st.button("Quitar último activo", use_container_width=True):
            st.session_state.watchlist.pop()
            st.rerun()

elif "Explorar mercado" in section:
    heading("02 / EXPLORADOR", "Mercado de activos digitales",
            "Comparación de precios públicos de CoinGecko." if MARKET_LIVE
            else "Comparación ilustrativa con datos simulados; la API no está disponible.")
    a, b = st.columns(2)
    with a:
        left_symbol = st.selectbox("Primer activo", COINS.keys(), index=0)
    with b:
        right_symbol = st.selectbox("Segundo activo", COINS.keys(), index=1)
    if left_symbol == right_symbol:
        st.info("Selecciona dos activos diferentes para compararlos.")
    else:
        c1, c2 = st.columns(2)
        for box, sym in ((c1, left_symbol), (c2, right_symbol)):
            coin = COINS[sym]
            with box:
                st.markdown(metric_card(coin["name"], f"US$ {coin['price']:,.2f}", f"{coin['change']:+.2f}%", coin["change"] >= 0, sym), unsafe_allow_html=True)
        fig = go.Figure()
        chart_ready = True
        for sym in (left_symbol, right_symbol):
            df = historical_series(sym, 30)
            if df is None:
                chart_ready = False
                break
            normalized = df["Precio"] / df["Precio"].iloc[0] * 100
            fig.add_trace(go.Scatter(x=df["Fecha"], y=normalized, mode="lines", name=sym, line={"width": 3, "color": COINS[sym]["color"]}))
        if chart_ready:
            fig.update_layout(height=360, title="Rendimiento relativo · base 100" + (" · CoinGecko" if MARKET_LIVE else " · simulado"),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font={"color":"#C1CAD7"}, legend={"orientation":"h"}, xaxis={"showgrid":False},
                              yaxis={"gridcolor":"rgba(126,157,189,0.13)"}, margin={"l":10,"r":10,"t":60,"b":20})
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("No se ha podido obtener el histórico real para ambos activos. No se presentan datos inventados.")
    st.markdown("### Tabla de referencia" + (" (CoinGecko)" if MARKET_LIVE else " (datos simulados)"))
    df = pd.DataFrame([{
        "Símbolo": sym, "Activo": c["name"], "Precio (USD)" if MARKET_LIVE else "Precio simulado (USD)": c["price"],
        "Cambio 24 h (%)" if MARKET_LIVE else "Cambio simulado (%)": c["change"],
        "Capitalización (miles de millones USD)" if MARKET_LIVE else "Capitalización ficticia (miles de millones USD)": c["market_cap"]
    } for sym, c in COINS.items()])
    st.dataframe(df, hide_index=True, use_container_width=True)

elif "Noticias" in section:
    heading("03 / INTELIGENCIA", "Noticias y contexto", "Las siguientes tarjetas son ejemplos de diseño, no noticias verificadas.")
    for item in DEMO_NEWS:
        st.markdown(
            f'<article class="news-card"><div class="news-meta"><span>{safe(item["tag"])} · EJEMPLO FICTICIO</span><span>{safe(item["time"])} (simulado)</span></div>'
            f'<h3>{safe(item["title"])}</h3><p>{safe(item["description"])}</p></article>', unsafe_allow_html=True
        )
    st.info("Integración futura: API de noticias con una licencia compatible con su uso público o comercial.")

elif "Asistente IA" in section:
    heading("04 / LABORATORIO", "Conversa con CryptoAnalyst",
            "Consultas por reglas con datos de CoinGecko; el agente IA con LangGraph todavía no está conectado." if MARKET_LIVE
            else "Prototipo de chat por reglas. Aún no utiliza un modelo de IA ni LangGraph.")
    st.markdown(
        '<div class="chat-context">◈ ASISTENTE POR REGLAS · '
        + ('COTIZACIONES COINGECKO' if MARKET_LIVE else 'RESPUESTAS SIMULADAS')
        + ' · NO ES ASESORÍA FINANCIERA</div>', unsafe_allow_html=True
    )
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ejemplo: compara Bitcoin con Ethereum..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        response = answer_market(prompt, selected, COINS) if MARKET_LIVE else answer_demo(prompt, selected)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    if st.button("Borrar conversación de demostración"):
        st.session_state.chat_history = []
        st.rerun()

elif "Arquitectura" in section:
    heading("05 / INGENIERÍA", "Arquitectura del producto", "Arquitectura por etapas: mercado real, análisis y agente inteligente.")
    st.markdown('''
<div class="arch-row"><div class="arch-node">USUARIO <small>Streamlit · interfaz</small></div><div class="arch-arrow">→</div><div class="arch-node">AGENTE <small>Python · LangGraph</small></div><div class="arch-arrow">→</div><div class="arch-node">HERRAMIENTAS <small>APIs · análisis</small></div></div>
''', unsafe_allow_html=True)
    st.markdown("""
**Estado actual:** la aplicación intenta consultar cotizaciones e históricos verificables de CoinGecko, usando caché y manejo de errores. Si el proveedor falla, se identifica explícitamente el modo demostración. Las noticias siguen siendo ejemplos; el chat usa reglas, NO un modelo de IA.

**Siguiente etapa:** obtener cotizaciones verificables de FreeCryptoAPI; conectar noticias con condiciones de uso apropiadas; añadir un modelo de lenguaje y memoria de conversación mediante LangGraph.

**Para producción:** autenticación de usuarios, registros de auditoría, caché de peticiones, manejo de errores y límites, pagos, protección de claves y verificación de licencias de los datos utilizados.
""")

footer_note = ("COTIZACIONES: COINGECKO CON CACHÉ · NOTICIAS DE EJEMPLO · CHAT POR REGLAS" if MARKET_LIVE
               else "API NO DISPONIBLE · TODOS LOS PRECIOS, VARIACIONES Y NOTICIAS MOSTRADOS SON FICTICIOS")
st.markdown(f'<div class="disclaimer">CRYPTOANALYST AI · PROTOTIPO ACADÉMICO · {footer_note}. NO CONSTITUYE ASESORÍA FINANCIERA.</div>', unsafe_allow_html=True)
