"""CryptoAnalyst AI Pro — plataforma privada de análisis cripto."""
from __future__ import annotations

from pathlib import Path
from uuid import uuid4
import time
import html
import os
import requests
import xml.etree.ElementTree as ET
from agent365 import ask as ask_agent, configured as ai_configured
from auth365 import AuthError, durable_accounts, provider, register, sign_in, verify_remote_session
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


def require_account() -> None:
    """Todo el sitio, incluido el acceso a datos y herramientas, requiere sesión."""
    user = st.session_state.get("auth_user")
    if isinstance(user, dict) and user.get("id"):
        if user.get("provider") == "supabase":
            checked = st.session_state.get("auth_checked_at", 0.0)
            if time.monotonic() - checked > 120:
                if not verify_remote_session(user):
                    st.session_state.pop("auth_user", None)
                    st.session_state.pop("auth_checked_at", None)
                    st.rerun()
                st.session_state.auth_checked_at = time.monotonic()
        return

    st.markdown("""
    <style>
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"]{display:none!important}
    [data-testid="stMainBlockContainer"]{max-width:1190px!important;padding-top:3.1rem!important}
    </style>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.09, 0.91], gap="large", vertical_alignment="center")
    with left:
        st.markdown("""
        <div class="auth-brand"><div class="auth-brand-symbol">◈</div>
          <div>CRYPTO<span>ANALYST</span><small>PRO INTELLIGENCE</small></div>
        </div>
        <div class="auth-eyebrow"><span class="auth-live-dot"></span> PLATAFORMA DE INTELIGENCIA CRIPTO</div>
        <h1 class="auth-headline">Invierte en<br><em>conocimiento.</em><br>No en suposiciones.</h1>
        <p class="auth-description">Una terminal inteligente para investigar activos digitales,
        comparar el mercado y explorar tendencias con datos trazables y herramientas de IA.</p>
        <div class="auth-feature-grid">
            <div><strong>01</strong><span>Mercado y gráficos</span></div>
            <div><strong>02</strong><span>Indicadores técnicos</span></div>
            <div><strong>03</strong><span>Agente de análisis IA</span></div>
            <div><strong>04</strong><span>Cartera virtual</span></div>
        </div>
        <div class="auth-trust">◉ ACCESO PRIVADO <span>·</span> ◇ DATOS IDENTIFICADOS <span>·</span> ↗ FREE / PRO</div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="auth-form-heading"><span>ACCESO A LA PLATAFORMA</span>
        <h2>Tu terminal, tu espacio.</h2>
        <p>Ingresa con tu cuenta o crea una nueva en menos de un minuto.</p></div>
        """, unsafe_allow_html=True)
        login_tab, register_tab = st.tabs(["Iniciar sesión", "Crear cuenta"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Correo electrónico", placeholder="nombre@correo.com",
                                      key="login_email", autocomplete="email")
                password = st.text_input("Contraseña", type="password",
                                         placeholder="Tu contraseña", key="login_password")
                submit = st.form_submit_button("Entrar al panel  →", use_container_width=True, type="primary")
            if submit:
                try:
                    st.session_state.auth_user = sign_in(email, password)
                    st.session_state.auth_checked_at = time.monotonic()
                    st.rerun()
                except AuthError as exc:
                    st.error(str(exc))
        with register_tab:
            with st.form("register_form"):
                full_name = st.text_input("Nombre completo", placeholder="Tu nombre y apellido",
                                          key="register_name")
                new_email = st.text_input("Correo electrónico", placeholder="nombre@correo.com",
                                           key="register_email", autocomplete="email")
                new_password = st.text_input("Crear contraseña", type="password",
                                              placeholder="Mínimo 12 caracteres, letras y números",
                                              key="register_password")
                confirm_password = st.text_input("Confirmar contraseña", type="password",
                                                  placeholder="Repite tu contraseña",
                                                  key="register_confirm")
                submit_register = st.form_submit_button(
                    "Crear cuenta gratuita  →", use_container_width=True, type="primary"
                )
            if submit_register:
                if new_password != confirm_password:
                    st.error("Las contraseñas no coinciden.")
                else:
                    try:
                        account = register(full_name, new_email, new_password)
                        if account.get("confirmation_required"):
                            st.success("Registro recibido. Verifica tu correo y después inicia sesión.")
                        else:
                            st.session_state.auth_user = account
                            st.session_state.auth_checked_at = time.monotonic()
                            st.rerun()
                    except AuthError as exc:
                        st.error(str(exc))
        try:
            persistent = durable_accounts()
        except AuthError as exc:
            st.error(str(exc))
            persistent = False
        if persistent:
            st.caption("Las cuentas se gestionan mediante Supabase Auth.")
        else:
            st.caption("Versión de prueba: las cuentas locales pueden borrarse al reiniciar el servidor. Usa una contraseña exclusiva para esta aplicación.")
        st.markdown('<div class="auth-legal">CryptoAnalyst AI Pro · Acceso privado · Plataforma de investigación, no asesoría financiera.</div>',
                    unsafe_allow_html=True)

    st.stop()


require_account()


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


if "agent_thread_id" not in st.session_state:
    st.session_state.agent_thread_id = str(uuid4())
if "wallet" not in st.session_state:
    st.session_state.wallet = {"cash": 10000.0, "positions": {}, "trades": []}

@st.cache_data(ttl=900, show_spinner=False)
def public_headlines():
    feeds = [
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Cointelegraph", "https://cointelegraph.com/rss"),
    ]
    items = []
    for provider, url in feeds:
        try:
            response = requests.get(url, timeout=8, headers={"User-Agent": "CryptoAnalyst-Education/1.0"})
            response.raise_for_status()
            root = ET.fromstring(response.content)
            for item in root.findall(".//item")[:6]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                date = item.findtext("pubDate", "").strip()
                if title and link.startswith("https://"):
                    items.append({"title": title, "url": link, "date": date, "source": provider})
        except (requests.RequestException, ET.ParseError):
            continue
    return items[:10]

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
        ["◫  Panel principal", "◈  Explorar mercado", "⌁  Análisis técnico", "▧  Cartera virtual", "▤  Noticias", "✦  Asistente IA", "◆  Planes Free / Pro", "⌘  Arquitectura"],
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
    current_user = st.session_state["auth_user"]
    user_name = html.escape(str(current_user.get("name", "Usuario")))
    user_email = html.escape(str(current_user.get("email", "")))
    st.markdown(
        f'<div class="account-card"><div class="account-avatar">◈</div>'
        f'<div><strong>{user_name}</strong><small>{user_email}</small></div>'
        f'<span class="account-tier">FREE</span></div>',
        unsafe_allow_html=True,
    )
    if st.button("Cerrar sesión", use_container_width=True, key="logout_button"):
        st.session_state.clear()
        st.rerun()
    st.markdown('<div class="sidebar-footer">v0.4 · Acceso privado · LangGraph<br>Python · Streamlit · OpenAI</div>', unsafe_allow_html=True)


st.markdown(
    '<div class="top-line"><span class="crumb">PRODUCTO / CRYPTOANALYST AI</span>'
    f'<span class="demo-pill">● {"MERCADO REAL · COINGECKO" if MARKET_LIVE else "MODO DEMO · DATOS SIMULADOS"}</span></div>', unsafe_allow_html=True
)

if "Panel principal" in section:
    st.markdown(
        '<div class="hero"><div class="hero-badge">◈ INTELIGENCIA DE MERCADO</div>'
        '<h1>El mercado, con una <span>nueva perspectiva.</span></h1>'
        '<p>Explora activos digitales, visualiza tendencias y conversa con un asistente. '
        'Un espacio personal para explorar indicadores, interpretar tendencias y desarrollar estrategias de análisis.</p>'
        '<div class="hero-footer"><span>● ACCESO PRIVADO</span><span>PYTHON · ANALÍTICA · AGENTES IA</span></div>'
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

elif "Análisis técnico" in section:
    heading("03 / INDICADORES", "Análisis técnico de mercado", "RSI, medias móviles y volatilidad calculados exclusivamente sobre datos externos observados.")
    if not MARKET_LIVE:
        st.warning("El proveedor de precios no responde: no calculamos indicadores usando datos ficticios.")
    else:
        sym = st.selectbox("Activo para análisis", list(COINS), index=list(COINS).index(selected), key="tech_symbol")
        history = cached_history(sym, 90, MARKET_KEY)
        if history is None or len(history) < 22:
            st.warning("El histórico observado no tiene suficientes datos para calcular los indicadores.")
        else:
            history = history.sort_values("Fecha").copy()
            p = pd.to_numeric(history["Precio"], errors="coerce").dropna()
            ret = p.pct_change()
            change = p.diff()
            up = change.clip(lower=0).rolling(14).mean()
            down = (-change.clip(upper=0)).rolling(14).mean()
            rs = up / down.replace(0, float("nan"))
            rsi = 100 - 100 / (1 + rs)
            sma7 = p.rolling(7).mean()
            sma21 = p.rolling(21).mean()
            vol = ret.std() * (365 ** 0.5) * 100
            a, b, c, d = st.columns(4)
            a.metric("Precio observado", f"US$ {p.iloc[-1]:,.2f}")
            b.metric("RSI (14)", f"{rsi.iloc[-1]:.1f}" if pd.notna(rsi.iloc[-1]) else "N/D")
            c.metric("SMA (21)", f"US$ {sma21.iloc[-1]:,.2f}" if pd.notna(sma21.iloc[-1]) else "N/D")
            d.metric("Volatilidad anualizada", f"{vol:.1f}%" if pd.notna(vol) else "N/D")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=history["Fecha"], y=p, name="Precio", mode="lines", line={"color":"#2dd4bf","width":3}))
            fig.add_trace(go.Scatter(x=history["Fecha"], y=sma7, name="SMA 7", line={"color":"#f59e0b","width":2}))
            fig.add_trace(go.Scatter(x=history["Fecha"], y=sma21, name="SMA 21", line={"color":"#9b8afB","width":2}))
            fig.update_layout(height=410, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font={"color":"#96A7BD"}, legend={"orientation":"h"}, yaxis={"tickprefix":"$"})
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Cálculos educativos sobre observaciones CoinGecko; no son recomendaciones de inversión.")

elif "Cartera virtual" in section:
    heading("04 / SIMULACIÓN", "Cartera de inversión virtual", "Simulador con capital ficticio de US$ 10.000; no permite comprar criptomonedas reales.")
    wallet = st.session_state.wallet
    positions = wallet["positions"]
    st.metric("Efectivo virtual", f"US$ {wallet['cash']:,.2f}")
    if not MARKET_LIVE:
        st.warning("Operaciones deshabilitadas porque no hay cotizaciones reales verificadas.")
    else:
        with st.form("trade_form", clear_on_submit=False):
            t1, t2, t3 = st.columns(3)
            action = t1.selectbox("Operación", ["Comprar", "Vender"])
            coin = t2.selectbox("Activo", list(COINS), key="trade_coin")
            amount = t3.number_input("Unidades", min_value=0.000001, value=0.01, step=0.01, format="%.6f")
            done = st.form_submit_button("Ejecutar operación simulada")
        if done:
            price = float(COINS[coin]["price"])
            cost = price * amount
            existing = float(positions.get(coin, 0.0))
            if action == "Comprar" and cost > wallet["cash"]:
                st.error("Saldo virtual insuficiente.")
            elif action == "Vender" and amount > existing:
                st.error("No tienes suficientes unidades virtuales.")
            else:
                wallet["cash"] += -cost if action == "Comprar" else cost
                positions[coin] = existing + amount if action == "Comprar" else existing - amount
                wallet["trades"].append({"Operación": action, "Activo": coin, "Unidades": amount,
                                         "Precio USD": price, "Total USD": cost})
                st.success("Operación virtual registrada en esta sesión.")
    if positions:
        rows = [{"Activo": sym, "Unidades": round(qty, 6),
                 "Valor USD": round(qty * COINS[sym]["price"], 2) if MARKET_LIVE else None}
                for sym, qty in positions.items() if qty > 0]
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    if wallet["trades"]:
        st.subheader("Historial de simulación")
        trades = pd.DataFrame(wallet["trades"])
        st.dataframe(trades, hide_index=True, use_container_width=True)
        st.download_button("Exportar operaciones CSV", data=trades.to_csv(index=False).encode(),
                           file_name="cartera_virtual.csv", mime="text/csv")
    st.caption("La cartera es temporal por sesión; todavía no se almacena en una cuenta persistente.")

elif "Noticias" in section:
    heading("05 / INFORMACIÓN", "Actualidad del mercado", "Titulares RSS de sus medios de origen, con atribución y enlace a la fuente.")
    articles = public_headlines()
    if not articles:
        st.warning("No se pudieron verificar titulares actuales desde los proveedores. No se mostrarán noticias ficticias.")
    else:
        for item in articles:
            st.markdown(f"**{safe(item['title'])}**")
            st.caption(f"{item['source']} · {item['date']}")
            st.link_button("Leer en la fuente", item["url"])

elif "Asistente IA" in section:
    heading("06 / AGENTE INTELIGENTE", "CryptoAnalyst — agente ReAct", "OpenAI + LangGraph + herramientas de mercado, noticias y memoria por conversación.")
    if ai_configured():
        st.success("Motor OpenAI configurado. El agente invocará herramientas cuando sean necesarias.")
    else:
        st.warning("OPENAI_API_KEY todavía no está configurada en Streamlit Secrets. El agente real está integrado, pero no se ejecutan respuestas inventadas.")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Consulta: compara BTC y ETH con datos actuales...", disabled=not ai_configured())
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.spinner("Consultando herramientas y modelo..."):
            try:
                response, used = ask_agent(prompt, st.session_state.agent_thread_id)
                if used:
                    response += "\n\n_Herramientas consultadas: " + ", ".join(used) + "_"
            except Exception as exc:
                response = "No se pudo completar la consulta del agente. Comprueba la clave OpenAI, créditos, proveedor y conectividad. (" + type(exc).__name__ + ")"
        st.session_state.chat_history.append({"role": "assistant", "content": str(response)})
        st.rerun()
    if st.button("Nueva conversación"):
        st.session_state.agent_thread_id = str(uuid4())
        st.session_state.chat_history = []
        st.rerun()
    st.caption("Memoria durante la sesión activa. Se requiere una base de datos persistente para cuentas comerciales.")

elif "Planes Free / Pro" in section:
    heading("07 / PRODUCTO", "Planes de CryptoAnalyst", "Diseño freemium para la futura versión comercial. No se realizan cobros desde esta demostración pública.")
    left, right = st.columns(2)
    with left:
        st.subheader("Free")
        st.markdown("Panel de mercado, comparador, indicadores y cartera virtual de sesión.")
        st.info("Tu cuenta Free incluye las herramientas disponibles del prototipo.")
    with right:
        st.subheader("Pro · Próximamente")
        st.markdown("Agente ReAct, memoria persistente, cuentas individuales y mayores cuotas de consulta.")
        st.info("Integración de pasarela y verificación de pagos preparada en el proyecto FastAPI, pero no desplegada en Streamlit Cloud.")
    st.caption("Ninguna suscripción está activa. Los pagos reales requieren backend, credenciales mercantiles y webhooks verificados.")

elif "Arquitectura" in section:
    heading("05 / INGENIERÍA", "Arquitectura del producto", "Arquitectura por etapas: mercado real, análisis y agente inteligente.")
    st.markdown('''
<div class="arch-row"><div class="arch-node">USUARIO <small>Streamlit · interfaz</small></div><div class="arch-arrow">→</div><div class="arch-node">AGENTE <small>Python · LangGraph</small></div><div class="arch-arrow">→</div><div class="arch-node">HERRAMIENTAS <small>APIs · análisis</small></div></div>
''', unsafe_allow_html=True)
    st.markdown("""
**Estado actual:** mercado CoinGecko, indicadores, cartera simulada, noticias RSS y agente ReAct con tres herramientas. El agente solo se habilita con credenciales privadas configuradas; en su ausencia no hay respuestas generativas.

**Siguiente etapa:** activar las credenciales de OpenAI y proveedores de noticias con licencias adecuadas; habilitar backend persistente y cuentas verificadas.

**Para producción:** autenticación de usuarios, registros de auditoría, caché de peticiones, manejo de errores y límites, pagos, protección de claves y verificación de licencias de los datos utilizados.
""")

footer_note = ("COTIZACIONES: COINGECKO · AGENTE LANGGRAPH REQUIERE CLAVE OPENAI · MONETIZACIÓN PENDIENTE" if MARKET_LIVE
               else "MERCADO NO DISPONIBLE · PRECIOS SIMULADOS IDENTIFICADOS COMO DEMO · MONETIZACIÓN PENDIENTE")
st.markdown(f'<div class="disclaimer">CRYPTOANALYST AI · PROTOTIPO ACADÉMICO · {footer_note}. NO CONSTITUYE ASESORÍA FINANCIERA.</div>', unsafe_allow_html=True)
