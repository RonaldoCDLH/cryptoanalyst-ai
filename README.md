# CryptoAnalyst AI Pro · Registro obligatorio + diseño Aurora

URL de la aplicación: https://cryptoanalyst-ronaldo2026.streamlit.app/

## Solución a `NotFoundError: removeChild` en Microsoft Edge

La interfaz de Streamlit es una aplicación React. **La traducción automática del navegador puede alterar los nodos del DOM** y causar el error `NotFoundError: Failed to execute 'removeChild' on 'Node'`, especialmente cuando se cambia entre páginas. El proyecto ya está redactado en español; no necesita traducción. Al menos en Streamlit Community Cloud, el idioma `lang` del documento puede continuar marcado internamente como inglés.

Si sucede:

1. En Edge, haz clic en el icono de traducción de la barra de direcciones y elige **Mostrar original**.
2. En las opciones de ese mismo icono, selecciona **Nunca traducir este sitio**.
3. Actualiza la página usando **Ctrl + F5**.

El código incluye `translate="no"` en los fragmentos HTML propios, lo que reduce la traducción de esos elementos, pero **no puede controlar los widgets internos de Streamlit ni la configuración de Edge**. Si el error persiste sin traducción, examinar extensiones que alteren la página y los registros del navegador.

El panel del agente ya no incluye el mensaje antiguo de “chat por reglas” de versiones anteriores; el chat generativo solo está disponible después de configurar `OPENAI_API_KEY`.

## Acceso de usuarios

La aplicación **no muestra el panel ni realiza consultas al mercado sin una sesión iniciada**. Incluye formulario de registro (nombre, email y contraseña), inicio de sesión y botón de cierre de sesión. Las contraseñas se verifican usando PBKDF2-HMAC-SHA256 y una sal aleatoria cuando se usa la base SQLite local; no se guardan en texto plano.

La nueva interfaz incorpora una pantalla de acceso de dos columnas, identidad visual violeta/índigo/cian, paneles modernos, tarjetas responsive y navegación mejorada.

**Muy importante:** hay dos modos de autenticación:

- **Sin configuración adicional:** SQLite local para **demostraciones**. El usuario puede crear una cuenta y entrar, pero en Streamlit Community Cloud el disco es efímero: **las cuentas pueden desaparecer después de reinicios o despliegues. No utilizarlo para clientes reales**.
- **Cuentas persistentes recomendadas:** configura [Supabase Auth](https://supabase.com/docs/guides/auth) en los **Secrets de Streamlit Cloud** para registro e inicio de sesión respaldados por un servicio de autenticación real, con políticas de correo y recuperación administradas por el proveedor. Las credenciales se envían directamente al servicio Auth por HTTPS. Habilita la confirmación por correo y configura el dominio permitido y las restricciones de alta en Supabase.

Agrega en Streamlit Cloud → App settings → Secrets (NUNCA en este repositorio):

```toml
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_ANON_KEY = "TU_CLAVE_PUBLICA_O_ANON"
OPENAI_API_KEY = "TU_CLAVE_OPENAI"
COINGECKO_DEMO_API_KEY = ""
FREECRYPTO_TOKEN = ""
NEWSAPI_KEY = ""
NEWSAPI_COMMERCIAL_LICENSE_ACKNOWLEDGED = "false"
```

Para una prueba del login sin OpenAI deja la clave OpenAI sin configurar: mercado, análisis y cartera se mantienen accesibles después del registro; el agente indica claramente que está desactivado. **No pegues contraseñas, claves o tokens en GitHub ni los compartas por chat**.

## Alcance del proyecto 365 Data Science

- Mercado de criptomonedas con fuente CoinGecko o modo demo identificado.
- Gráficos interactivos y comparación de activos.
- Indicadores RSI, SMA7/SMA21 y volatilidad sobre datos observados.
- Cartera virtual educativa por sesión, no conectada a intercambios.
- Noticias RSS atribuidas; sin titulares de ejemplo presentados como actuales.
- Agente OpenAI/LangGraph con tres herramientas (lista, datos y noticias) y memoria temporal por hilo; requiere clave y créditos válidos.
- Propuesta de planes Free y Pro. **Monetización todavía no activada en esta URL**.

## Pruebas

GitHub Actions instala dependencias, comprueba sintaxis, importa el agente y ejecuta pruebas del registro, hash de contraseñas, duplicados y bloqueo del panel para usuarios anónimos.

## Pendientes antes de vender suscripciones

Cuentas persistentes y verificación de correo con Supabase, términos y política de datos, recuperación de cuenta, cuotas y controles contra abuso, API y memoria persistente por usuario, verificación de pagos y webhooks, licencias comerciales de noticias/datos y pruebas de infraestructura. El formulario Free/Pro es informativo y **no recibe pagos** todavía.

Esta aplicación no ofrece recomendaciones personales de inversión ni garantiza cotizaciones en tiempo real.
