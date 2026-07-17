import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# 1. Configuración de la página
st.set_page_config(
    page_title="Libres por Cristo", 
    page_icon="🎹", 
    layout="centered"
)

# Configura tu API Key de Google Gemini para la digitalización por foto
API_KEY_GEMINI = "AQ.Ab8RN6IAXg7a9i016k1D4hXuitiGsrN2Gy_qQ_ap68rPfLf17w"

if API_KEY_GEMINI != "AQUÍ_PEGA_TU_CLAVE":
    genai.configure(api_key=API_KEY_GEMINI)

# 2. SISTEMA DE BASE DE DATOS PERMANENTE (JSON)
ARCHIVO_BD = "cancionero.json"

# Canciones iniciales corregidas (ahora dicen Estrofa)
canciones_defecto = {
    "al que esta sentado": {
        "titulo_real": "Al que está sentado",
        "acordes": "Estrofa // D A D, Bm A D, Bm A D G // A\nCoro // D Bm G A, G A //"
    },
    "el gran yo soy": {
        "titulo_real": "El Gran Yo Soy",
        "acordes": "Estrofa // F# G#m C# F# //\nCoro // D#m B F# C#"
    },
    "santo por siempre": {
        "titulo_real": "Santo por siempre",
        "acordes": "Estrofa // F A# F Dm C F //\nPre coro // A# C Dm C A# //\nCoro // A# Dm C Am A Dm, Gm C F //"
    },
    "dios de lo imposible": {
        "titulo_real": "Dios de lo imposible",
        "acordes": "Estrofa // Cm G# D# A#, Cm G# D# A# //\nCoro // D# A# D# A# G# A# //"
    }
}

# Función para cargar canciones del disco duro
def cargar_cancionero():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return canciones_defecto
    else:
        guardar_cancionero(canciones_defecto)
        return canciones_defecto

# Función para guardar canciones en el disco duro de forma permanente
def guardar_cancionero(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Cargar los datos permanentes
cancionero = cargar_cancionero()

if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []

# Título principal
st.title("🎹 Lista de canciones libres por Cristo")

# ==========================================
# SECCIÓN: BARRA LATERAL (CREADOR DE LISTAS)
# ==========================================
with st.sidebar:
    st.header("📋 Lista para el Servicio")
    
    canciones_disponibles = [datos["titulo_real"] for datos in cancionero.values()]
    cancion_a_añadir = st.selectbox("Selecciona para añadir:", ["-- Seleccionar --"] + canciones_disponibles)
    
    if st.button("➕ Añadir a la lista") and cancion_a_añadir != "-- Seleccionar --":
        if cancion_a_añadir not in st.session_state.lista_servicio:
            st.session_state.lista_servicio.append(cancion_a_añadir)
            st.success(f"¡{cancion_a_añadir} añadida!")
        else:
            st.warning("Esta canción ya está en tu lista.")
            
    st.write("---")
    
    if st.session_state.lista_servicio:
        st.write("**Canciones para hoy:**")
        for i, cancion in enumerate(st.session_state.lista_servicio, 1):
            st.write(f"**{i}. {cancion}**")
            
        if st.button("🗑️ Limpiar lista"):
            st.session_state.lista_servicio = []
            st.rerun()
    else:
        st.info("Tu lista de hoy está vacía.")

# ==========================================
# PESTAÑAS PRINCIPALES: BUSCADOR VS AGREGAR
# ==========================================
pestana_buscar, pestana_agregar = st.tabs(["🔍 Buscar Canciones", "➕ Agregar Nueva Canción"])

# --- PESTAÑA 1: BUSCADOR ---
with pestana_buscar:
    busqueda = st.text_input("🔍 Busca el nombre de la canción o palabra clave:", "")
    busqueda_limpia = busqueda.lower().strip()

    if busqueda_limpia:
        coincidencias = []
        for clave in cancionero.keys():
            if busqueda_limpia in clave:
                coincidencias.append(clave)
                
        if len(coincidencias) == 0:
            st.error("❌ No se encontró ninguna canción con ese nombre.")
        elif len(coincidencias) == 1:
            cancion = cancionero[coincidencias[0]]
            st.subheader(f"🎵 {cancion['titulo_real']}")
            st.code(cancion['acordes'], language="text")
        else:
            st.warning("🔍 Encontré varias opciones en tu cuaderno. Elige una:")
            opciones_pantalla = [cancionero[c]["titulo_real"] for c in coincidencias]
            seleccion = st.selectbox("Elige la canción:", opciones_pantalla)
            
            for clave in coincidencias:
                if cancionero[clave]["titulo_real"] == seleccion:
                    st.subheader(f"🎵 {cancionero[clave]['titulo_real']}")
                    st.code(cancionero[clave]["acordes"], language="text")
                    break
    else:
        if st.session_state.lista_servicio:
            st.markdown("### 🎼 Guía rápida del Servicio de hoy")
            for nombre in st.session_state.lista_servicio:
                for clave, datos in cancionero.items():
                    if datos["titulo_real"] == nombre:
                        with st.expander(f"🎵 {nombre}", expanded=False):
                            st.code(datos["acordes"], language="text")
        else:
            st.info("Escribe arriba para buscar acordes.")

# --- PESTAÑA 2: AGREGAR CANCIÓN ---
with pestana_agregar:
    st.subheader("📝 Registra una nueva canción")
    
    metodo = st.radio("Elige cómo deseas agregarla:", ["Escribir manualmente", "Tomar una foto / Cargar Imagen 📸"])
    
    if metodo == "Escribir manualmente":
        nuevo_titulo = st.text_input("Nombre de la canción (Ej: Cuan grande es el):")
        nuevos_acordes = st.text_area("Estructura y acordes (Usa el formato de tu cuaderno con //):", placeholder="Estrofa // G C D //\nCoro // G C D //")
        
        if st.button("💾 Guardar Canción"):
            if nuevo_titulo and nuevos_acordes:
                clave_nueva = nuevo_titulo.lower().strip().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                
                cancionero[clave_nueva] = {
                    "titulo_real": nuevo_titulo.strip(),
                    "acordes": nuevos_acordes.strip()
                }
                guardar_cancionero(cancionero)
                st.success(f"¡{nuevo_titulo} guardada permanentemente!")
                st.rerun()
            else:
                st.error("Por favor completa el título y los acordes.")
                
    elif metodo == "Tomar una foto / Cargar Imagen 📸":
        if API_KEY_GEMINI == "AQUÍ_PEGA_TU_CLAVE":
            st.warning("⚠️ Configura tu API Key en la línea 15.")
        else:
            foto = st.file_uploader("Sube una foto o tómala con tu cámara:", type=["jpg", "jpeg", "png"])
            
            if foto is not None:
                imagen_original = Image.open(foto)
                
                if imagen_original.width > 1024:
                    proporcion = 1024 / float(imagen_original.width)
                    alto_nuevo = int((float(imagen_original.height) * float(proporcion)))
                    imagen_procesada = imagen_original.resize((1024, alto_nuevo), Image.Resampling.LANCZOS)
                else:
                    imagen_procesada = imagen_original
                
                st.image(imagen_procesada, caption="Foto optimizada", width=250)
                
                if st.button("🪄 Digitalizar con Inteligencia Artificial"):
                    with st.spinner("Leyendo tu cuaderno con IA..."):
                        try:
                            model = genai.GenerativeModel('gemini-1.5-flash')
                            # Instrucciones actualizadas para que la IA escriba Estrofa correctamente
                            instrucciones = """
                            Analiza la imagen de este cuaderno de acordes musicales. 
                            Extrae el título de la canción y los acordes correspondientes a cada sección (Estrofa, Pre coro, Coro).
                            Debes estructurar el resultado EXACTAMENTE con el siguiente formato, usando barras dobles '//' y comas para separar los acordes, idéntico a este ejemplo:
                            
                            Título: Nombre de la Canción
                            ---
                            Estrofa // D A D, Bm A D //
                            Coro // D Bm G A //
                            
                            No agregues letras de la canción ni explicaciones. Solo la estructura y los acordes con las barras dobles '//'. Es importante que uses la palabra 'Estrofa' y no 'Estropa'.
                            """
                            
                            respuesta = model.generate_content([instrucciones, imagen_procesada])
                            resultado_texto = respuesta.text
                            
                            lineas = resultado_texto.strip().split("\n")
                            titulo_detectado = "Nueva Canción"
                            acordes_detectados = ""
                            
                            guardando_acordes = False
                            for linea in lineas:
                                if "Título:" in linea or "Titulo:" in linea:
                                    titulo_detectado = linea.replace("Título:", "").replace("Titulo:", "").strip()
                                elif "---" in linea:
                                    guardando_acordes = True
                                elif guardando_acordes:
                                    acordes_detectados += linea + "\n"
                            
                            if not acordes_detectados:
                                acordes_detectados = resultado_texto
                                
                            st.session_state["temp_titulo"] = titulo_detectado
                            st.session_state["temp_acordes"] = acordes_detectados.strip()
                            
                        except Exception as e:
                            st.error(f"Error al procesar la imagen: {e}")
            
            if "temp_titulo" in st.session_state:
                st.write("---")
                st.subheader("🔍 Verifica el resultado de la IA:")
                
                titulo_final = st.text_input("Confirmar Título:", st.session_state["temp_titulo"])
                acordes_finales = st.text_area("Confirmar Acordes:", st.session_state["temp_acordes"], height=150)
                
                if st.button("💾 Guardar en el Cancionero Permanente"):
                    clave_nueva = titulo_final.lower().strip().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    
                    cancionero[clave_nueva] = {
                        "titulo_real": titulo_final.strip(),
                        "acordes": acordes_finales.strip()
                    }
                    guardar_cancionero(cancionero)
                    
                    st.success(f"¡{titulo_final} ha sido guardada para siempre!")
                    del st.session_state["temp_titulo"]
                    del st.session_state["temp_acordes"]
                    st.rerun()