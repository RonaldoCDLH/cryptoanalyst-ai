"""CryptoAnalyst AI — prototipo visual en Streamlit (modo demostración)."""
from __future__ import annotations

from pathlib import Path
import html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data import COINS, DEMO_NEWS, answer_demo, price_history

st.set_page_config(
    page_title="CryptoAnalyst AI | Terminal inteligente",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = (Path(__file__).parent / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["BTC", "ETH", "SOL"]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Bienvenido a **CryptoAnalyst AI**. Este es un **prototipo con datos simulados**. Pregúntame por Bitcoin, compara dos criptomonedas o consulta el módulo de noticias."}
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
        '<span> · ilustrativo</span></div></div>'
    )


def chart_for(symbol: str, days: int, height: int = 365) -> go.Figure:
    history = price_history(symbol, days)
    color = COINS[symbol]["color"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history["Fecha"], y=history["Precio"],
        name=symbol, mode="lines",
        line={"color": color, "width": 3.5, "shape": "spline"},
        fill="tozeroy", fillcolor="rgba(45,212,191,0.035)",
        hovertemplate="%{x|%d %b %Y}<br><b>US$ %{y:,.2f}</b> (simulado)<extra></extra>",
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
    st.markdown('<div class="sidebar-info"><div class="dot"></div><div><strong>Modo demostración</strong><br><span>Datos sintéticos · sin APIs</span></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">v0.1 · Prototipo académico<br>Construido con Python + Streamlit</div>', unsafe_allow_html=True)


st.markdown(
    '<div class="top-line"><span class="crumb">PRODUCTO / CRYPTOANALYST AI</span>'
    '<span class="demo-pill">● MODO DEMO · DATOS SIMULADOS</span></div>', unsafe_allow_html=True
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
    heading("01 / PANORAMA", "Vista general del mercado", "Cifras ficticias para validar la experiencia visual; todavía no son cotizaciones reales.")
    cols = st.columns(4, gap="medium")
    for idx, sym in enumerate(["BTC", "ETH", "SOL", "BNB"]):
        c = COINS[sym]
        with cols[idx]:
            st.markdown(metric_card(c["name"], f"US$ {c['price']:,.2f}", f"{c['change']:+.2f}%", c["change"] >= 0, sym), unsafe_allow_html=True)

    left, right = st.columns([1.84, 1], gap="large")
    with left:
        st.markdown('<div class="panel-heading"><div><span class="eyebrow">GRÁFICA EXPLORATORIA</span><h3>Evolución del precio</h3></div><span class="panel-badge">SERIE SINTÉTICA</span></div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown(f'<div class="selected-coin">{safe(COINS[selected]["name"])} <span>{safe(selected)}</span></div>', unsafe_allow_html=True)
        with c2:
            period = st.radio("Intervalo", ["7D", "30D", "90D"], index=1, horizontal=True, label_visibility="collapsed")
        st.plotly_chart(chart_for(selected, int(period[:-1])), use_container_width=True, config={"displayModeBar": False})
        st.caption("Visualización sintética; los valores no describen el mercado actual.")
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
    heading("02 / EXPLORADOR", "Mercado de activos digitales", "Comparación interactiva de activos con información totalmente simulada.")
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
        for sym in (left_symbol, right_symbol):
            df = price_history(sym, 30)
            normalized = df["Precio"] / df["Precio"].iloc[0] * 100
            fig.add_trace(go.Scatter(x=df["Fecha"], y=normalized, mode="lines", name=sym, line={"width": 3, "color": COINS[sym]["color"]}))
        fig.update_layout(height=360, title="Rendimiento relativo simulado · base 100", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color":"#C1CAD7"}, legend={"orientation":"h"}, xaxis={"showgrid":False}, yaxis={"gridcolor":"rgba(126,157,189,0.13)"}, margin={"l":10,"r":10,"t":60,"b":20})
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("### Tabla de referencia (datos de muestra)")
    df = pd.DataFrame([{
        "Símbolo": sym, "Activo": c["name"], "Precio simulado (USD)": c["price"],
        "Cambio simulado (%)": c["change"], "Capitalización ficticia (miles de millones USD)": c["market_cap"]
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
    heading("04 / LABORATORIO", "Conversa con CryptoAnalyst", "Prototipo de chat por reglas. Aún no utiliza un modelo de IA ni LangGraph.")
    st.markdown('<div class="chat-context">◈ VISTA PREVIA · RESPUESTAS SIMULADAS · NO ES ASESORÍA FINANCIERA</div>', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ejemplo: compara Bitcoin con Ethereum..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "assistant", "content": answer_demo(prompt, selected)})
        st.rerun()
    if st.button("Borrar conversación de demostración"):
        st.session_state.chat_history = []
        st.rerun()

elif "Arquitectura" in section:
    heading("05 / INGENIERÍA", "Arquitectura del producto", "Plan técnico para evolucionar este prototipo hacia un agente real y monetizable.")
    st.markdown('''
<div class="arch-row"><div class="arch-node">USUARIO <small>Streamlit · interfaz</small></div><div class="arch-arrow">→</div><div class="arch-node">AGENTE <small>Python · LangGraph</small></div><div class="arch-arrow">→</div><div class="arch-node">HERRAMIENTAS <small>APIs · análisis</small></div></div>
''', unsafe_allow_html=True)
    st.markdown("""
**Estado actual:** la interfaz, los gráficos, el comparador, la lista de seguimiento y el chat de prueba son funcionales con datos ilustrativos.

**Siguiente etapa:** obtener cotizaciones verificables de FreeCryptoAPI; conectar noticias con condiciones de uso apropiadas; añadir un modelo de lenguaje y memoria de conversación mediante LangGraph.

**Para producción:** autenticación de usuarios, registros de auditoría, caché de peticiones, manejo de errores y límites, pagos, protección de claves y verificación de licencias de los datos utilizados.
""")

st.markdown('<div class="disclaimer">CRYPTOANALYST AI · PROTOTIPO ACADÉMICO · TODOS LOS PRECIOS, VARIACIONES Y NOTICIAS MOSTRADOS SON FICTICIOS. NO CONSTITUYE ASESORÍA FINANCIERA.</div>', unsafe_allow_html=True)
