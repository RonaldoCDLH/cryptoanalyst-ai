# CryptoAnalyst AI

Prototipo visual académico hecho con Python, Streamlit y Plotly, con estética de terminal financiera y diseño responsive. La aplicación incluye un panel de seguimiento, gráficas interactivas, comparador de activos, lista de observación, tarjetas de noticias y un chat funcional por reglas.

**Advertencia importante:** esta versión utiliza datos de demostración inventados. No se conecta a mercados, NewsAPI, OpenAI ni LangGraph y no ofrece recomendaciones financieras. Los módulos reales se añadirán en las etapas siguientes del curso de 365 Data Science.

## Ejecutarlo en Windows 11 con VS Code

1. Extrae el archivo ZIP y abre la carpeta `CryptoAnalystAI` en VS Code.
2. Abre una terminal de PowerShell desde VS Code.
3. Crea un entorno virtual:

   ```powershell
   py -m venv .venv
   ```
4. Instala las dependencias:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
5. Ejecuta la aplicación:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

6. El navegador abrirá la dirección local (normalmente `http://localhost:8501`).

No es necesario configurar claves API para probar esta versión.

## Archivos

- `app.py`: interfaz y acciones.
- `styles.css`: identidad visual, tarjetas y paneles.
- `data.py`: cifras, series, noticias y respuestas simuladas.
- `requirements.txt`: dependencias para el prototipo.
- `.env.example`: plantilla vacía para futuras claves de API.
- `.gitignore`: evita publicar credenciales y archivos temporales.

## Evolución prevista

1. Implementar un cliente para FreeCryptoAPI con validaciones, caché y fecha/hora.
2. Integrar noticias bajo una licencia de datos adecuada al despliegue.
3. Crear herramientas de LangChain y un agente LangGraph con memoria.
4. Conectar el chat de Streamlit al agente real.
5. Implementar autenticación, monitoreo, límites de consumo y opciones de suscripción.

Antes de monetizar, verificar derechos de uso comercial de las APIs y requisitos jurídicos aplicables.
