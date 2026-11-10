# CryptoAnalyst AI Pro — edición pública Streamlit

Aplicación web académica basada en el proyecto de agente cripto de 365 Data Science. Se ejecuta en Streamlit Cloud: https://cryptoanalyst-ronaldo2026.streamlit.app/

## Funciones actuales

- Panel y explorador de mercado CoinGecko; cuando no hay acceso a cotizaciones se etiqueta el modo de datos demostrativos.
- Análisis técnico: RSI 14, medias móviles 7 y 21, volatilidad histórica calculada sobre datos observados.
- Cartera de inversión **virtual por sesión**, sin órdenes reales, sin persistencia entre sesiones.
- Noticias RSS de fuentes atribuidas (no se presentan ejemplos de titulares ficticios como si fueran noticias).
- Agente IA **real** con LangGraph `StateGraph`, `ToolNode`, herramientas `crypto_list_tool`, `crypto_data_tool`, `crypto_news_tool` y `ChatOpenAI`. Checkpointer en memoria **por sesión del proceso**, no base de datos de usuarios.
- Página de planes informativa Free/Pro. **No acepta pagos ni activa suscripciones** en Streamlit Cloud.

## Habilitar el agente

En Settings → Secrets de la aplicación Streamlit Cloud configura, sin publicarlas en este repositorio:

```toml
OPENAI_API_KEY = "tu_clave_privada_de_OpenAI"
COINGECKO_DEMO_API_KEY = ""
FREECRYPTO_TOKEN = ""
NEWSAPI_KEY = ""
NEWSAPI_COMMERCIAL_LICENSE_ACKNOWLEDGED = "false"
```

Solo `OPENAI_API_KEY` habilita el agente generativo. La clave de CoinGecko y FreeCryptoAPI son opcionales; NEWSAPI_KEY requiere permiso/licencia de uso comercial para el entorno público y un valor explícito `true` en `NEWSAPI_COMMERCIAL_LICENSE_ACKNOWLEDGED`. Nunca compartas claves en capturas o conversaciones.

El chat no simula OpenAI si falta la clave. El histórico de chat del navegador se conserva en la sesión Streamlit y las herramientas usan un checkpointer de proceso; para una plataforma multiusuario de producción hay que incorporar almacenamiento persistente y aislamiento autenticado.

## Ejecutar pruebas de integración y sintaxis

El workflow `.github/workflows/verify.yml` verifica imports del agente, sintaxis e instalación de dependencias en GitHub Actions. Los proveedores externos no se prueban sin claves.

## Monetización real: pendiente

La vista Free/Pro es una propuesta de producto. No hay login persistente ni pasarela de pagos conectada al servicio Streamlit. El paquete local con FastAPI (en la conversación de desarrollo) contiene un prototipo de autenticación y endpoints Stripe/Wompi, pero para activarlos en una aplicación pública hacen falta hosting de backend con HTTPS, variables secretas, webhook verificado, licencias, privacidad, tests de pago y controles de producción.

No se ofrecen recomendaciones personalizadas de inversión. Los datos públicos dependen de terceros y pueden tener retrasos.
