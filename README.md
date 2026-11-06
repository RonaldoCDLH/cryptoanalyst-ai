# CryptoAnalyst AI

Aplicación académica en Python y Streamlit para explorar el mercado de criptomonedas. Interfaz propia con CSS, gráficos Plotly, comparación de activos, lista de seguimiento, noticias de muestra y chat por reglas.

**Versión 0.2:** el panel ahora **intenta obtener precios y variaciones reales** de Bitcoin, Ethereum, Solana, BNB, XRP y Cardano mediante la API pública de CoinGecko. Las respuestas se almacenan en caché durante 5 minutos para reducir las solicitudes. Los históricos se almacenan durante 15 minutos. La aplicación identifica la fuente de datos usada.

Cuando la API está temporalmente inaccesible o limitada, la interfaz permanece disponible en **modo DEMO** con datos **ficticios identificados claramente**. Nunca presenta los datos inventados como cotizaciones actuales. Si no hay datos históricos reales, se explica el problema en lugar de inventar una gráfica.

**Aún no se ha integrado LangGraph, OpenAI, ni un servicio de noticias en producción.** El chat implementado funciona por reglas y las noticias actuales del panel son contenido ilustrativo, no titulares verificables. No debe presentarse como asesor de inversión ni como un agente IA de producción.

## App pública

https://cryptoanalyst-ronaldo2026.streamlit.app/

## Ejecución local en Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

La aplicación funciona en modo demo sin credenciales. Para consultar la API pública de CoinGecko no es obligatorio registrarse, aunque las peticiones están limitadas y pueden ser bloqueadas por IP. Una clave Demo gratuita opcional puede mejorar la disponibilidad.

Para usar una clave CoinGecko Demo opcional, añádela en el panel **Streamlit → Settings → Secrets** con este formato TOML:

```toml
COINGECKO_DEMO_API_KEY = "TU_CLAVE_PRIVADA_AQUI"
```

**Nunca publiques claves reales en GitHub, README, capturas ni conversaciones.** Para trabajar localmente también puedes configurar la variable de entorno `COINGECKO_DEMO_API_KEY`.

## Estructura

- `app.py`: interfaz de Streamlit y lógica de navegación.
- `styles.css`: apariencia de la plataforma.
- `data.py`: datos sintéticos de respaldo y respuestas de demostración.
- `services/market_data.py`: cotizaciones reales, históricos, validaciones, manejo de errores y respuestas por reglas basadas en datos.
- `requirements.txt`: dependencias instaladas automáticamente por Streamlit.
- `.gitignore`: protección de archivos de claves, entornos y caché.

## Próximos pasos para igualar el proyecto de 365 Data Science

1. Conectar la API FreeCryptoAPI mediante una clave privada y verificar su licencia de uso.
2. Incorporar un servicio de noticias cuya licencia permita el uso en una app pública. El plan Developer gratuito de NewsAPI **no permite producción**.
3. Implementar las tres herramientas de consulta, el agente ReAct en LangGraph y memoria por conversación.
4. Activar un LLM opcional mediante claves seguras en Streamlit Secrets.
5. Crear pruebas automáticas, monitoreo, límites de llamadas y documentación de sustentación.

CoinGecko: https://www.coingecko.com/en/api

No se garantizan precios en tiempo real ni ganancias financieras. Consulta los datos directamente en la fuente antes de tomar decisiones.
