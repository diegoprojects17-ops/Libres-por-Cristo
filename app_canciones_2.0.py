import os
import google.generativeai as genai
import requests
import streamlit as st
from PIL import Image

# 1. Configuración de la página
st.set_page_config(
    page_title="Acordes & Oración",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estética estilo Dark Mode para móvil
st.markdown(
    """
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .song-box {
        background-color: #1e293b;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .chord-line {
        font-family: 'Courier New', monospace;
        color: #f59e0b;
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎵 Cancionero de Oración")

# 2. Configuración de Claves desde los Secrets de Streamlit
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
JSONBIN_BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "")
JSONBIN_API_KEY = st.secrets.get("JSONBIN_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# 3. Funciones para la Base de Datos (JSONBin)
def cargar_canciones():
    if not JSONBIN_BIN_ID or not JSONBIN_API_KEY:
        return []
    headers = {"X-Master-Key": JSONBIN_API_KEY}
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get("record", {}).get("canciones", [])
    except Exception as e:
        st.error(f"Error de conexión con JSONBin: {e}")
    return []


def guardar_canciones(lista_canciones):
    if not JSONBIN_BIN_ID or not JSONBIN_API_KEY:
        st.error("Faltan las credenciales de JSONBin en Secrets.")
        return False
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_API_KEY,
    }
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
    data = {"canciones": lista_canciones}
    try:
        res = requests.put(url, json=data, headers=headers)
        return res.status_code == 200
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


# Inicializar estado
if "canciones" not in st.session_state:
    st.session_state["canciones"] = cargar_canciones()

pestana1, pestana2, pestana3 = st.tabs(
    ["📖 Repertorio", "🪄 Escanear Foto", "➕ Agregar Manual"]
)

# --- PESTAÑA 1: VER REPERTORIO ---
with pestana1:
    canciones = st.session_state["canciones"]
    if canciones:
        titulos = [c["titulo"] for c in canciones]
        seleccion = st.selectbox("Selecciona una canción:", titulos)
        cancion = next(c for c in canciones if c["titulo"] == seleccion)

        st.subheader(cancion["titulo"])
        st.caption(
            f"Tono: **{cancion.get('tono', 'N/A')}** | Ritmo: **{cancion.get('ritmo', 'N/A')}**"
        )
        st.divider()

        # Renderizado de contenido
        if "secciones" in cancion and isinstance(cancion["secciones"], list):
            for sec in cancion["secciones"]:
                st.markdown(
                    f"""
                    <div class="song-box">
                        <strong style="color: #38bdf8;">{sec.get('nombre', 'Sección')}</strong><br>
                        <div class="chord-line">{sec.get('acordes', '').replace('\n', '<br>')}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.code(cancion.get("contenido", ""), language="text")
    else:
        st.info("No hay canciones registradas aún.")

# --- PESTAÑA 2: TRANSCRIBIR FOTO CON GEMINI ---
with pestana2:
    st.subheader("Digitalizar cuaderno con IA")
    imagen_archivo = st.file_uploader(
        "Sube una foto del cuaderno:", type=["jpg", "jpeg", "png"]
    )

    if imagen_archivo:
        imagen = Image.open(imagen_archivo)
        st.image(
            imagen, caption="Imagen cargada", use_container_width=True
        )

        if st.button("🪄 Transcribir Acordes"):
            if not GEMINI_API_KEY:
                st.error("Configura tu GEMINI_API_KEY en los Secrets.")
            else:
                with st.spinner("Procesando imagen con Gemini..."):
                    try:
                        # ✅ CORRECCIÓN CLAVE: Uso del endpoint 'gemini-1.5-flash-latest'
                        model = genai.GenerativeModel("gemini-1.5-flash-latest")

                        prompt = """
                        Analiza la imagen de esta hoja de música/acordes.
                        Extrae el título de la canción y la estructura de acordes.
                        Responde estrictamente con el siguiente formato:
                        
                        Título: [Nombre de la canción]
                        Tono: [Nota]
                        Ritmo: [Ritmo o compás]
                        
                        ---
                        [Escribe aquí las estrofas y acordes ordenados]
                        """

                        respuesta = model.generate_content([prompt, imagen])
                        st.session_state["resultado_transcripcion"] = (
                            respuesta.text
                        )
                        st.success("¡Transcripción completada con éxito!")

                    except Exception as e:
                        st.error(
                            f"Error al conectar con la API de Gemini: {e}"
                        )

    # Mostrar resultado transcrito y guardar
    if "resultado_transcripcion" in st.session_state:
        st.divider()
        st.text_area(
            "Resultado obtenido:",
            st.session_state["resultado_transcripcion"],
            height=200,
        )

        titulo_guardar = st.text_input(
            "Confirmar título para guardar:", key="titulo_ia"
        )
        if st.button("💾 Guardar en la Base de Datos"):
            if titulo_guardar:
                nueva_cancion = {
                    "titulo": titulo_guardar,
                    "tono": "Por definir",
                    "ritmo": "Por definir",
                    "contenido": st.session_state["resultado_transcripcion"],
                }
                st.session_state["canciones"].append(nueva_cancion)

                if guardar_canciones(st.session_state["canciones"]):
                    st.success("¡Canción guardada permanentemente!")
                    del st.session_state["resultado_transcripcion"]
                    st.rerun()
            else:
                st.warning("Escribe un título antes de guardar.")

# --- PESTAÑA 3: AGREGAR MANUALMENTE ---
with pestana3:
    st.subheader("Agregar canción manualmente")
    nuevo_titulo = st.text_input("Título de la canción:")
    nuevo_tono = st.text_input("Tono (ej: G, C, Am):")
    nuevo_ritmo = st.text_input("Ritmo (ej: 4/4 Balada):")
    nuevo_contenido = st.text_area(
        "Acordes / Estructura:",
        height=150,
        placeholder="Intro: | G | C |\nEstrofa: G - C - D",
    )

    if st.button("💾 Guardar Canción"):
        if nuevo_titulo and nuevo_contenido:
            cancion_nueva = {
                "titulo": nuevo_titulo,
                "tono": nuevo_tono,
                "ritmo": nuevo_ritmo,
                "contenido": nuevo_contenido,
            }
            st.session_state["canciones"].append(cancion_nueva)

            if guardar_canciones(st.session_state["canciones"]):
                st.success("¡Canción agregada con éxito!")
                st.rerun()
        else:
            st.warning("El título y el contenido son obligatorios.")
