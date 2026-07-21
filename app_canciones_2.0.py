import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(
    page_title="Libres por Cristo", 
    page_icon="🎹", 
    layout="centered"
)

# Estilo visual adaptado para el escenario
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    div[data-testid="stCodeBlock"] {
        background-color: #020617 !important;
        border-left: 5px solid #38bdf8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Configura tu API Key de Google Gemini
API_KEY_GEMINI = "AQ.Ab8RN6IAXg7a9i016k1D4hXuitiGsrN2Gy_qQ_ap68rPfLf17w"

if API_KEY_GEMINI != "AQUÍ_PEGA_TU_CLAVE":
    genai.configure(api_key=API_KEY_GEMINI)

# 2. BASE DE DATOS PERMANENTE (JSON)
ARCHIVO_BD = "cancionero.json"

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

def cargar_datos():
    if os.path.exists(ARCHIVO_BD):
        try:
            with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
                datos = json.load(f)
                if "canciones" not in datos:
                    return {"canciones": datos, "calendario": {}}
                return datos
        except:
            return {"canciones": canciones_defecto, "calendario": {}}
    else:
        estructura = {"canciones": canciones_defecto, "calendario": {}}
        guardar_datos(estructura)
        return estructura

def guardar_datos(datos):
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

# Cargar la base de datos
db = cargar_datos()
cancionero = db["canciones"]
calendario = db["calendario"]

if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []

# Encabezado con diseño estilizado
st.markdown(
    """
    <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #f8fafc; margin: 0; font-size: 26px;'>🎹 Libres por Cristo</h1>
        <p style='color: #38bdf8; margin: 5px 0 0 0; font-size: 14px;'>Cancionero Digital & Agenda del Ministerio</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# ==========================================
# BARRA LATERAL (CREADOR DE LISTAS RÁPIDAS)
# ==========================================
with st.sidebar:
    st.header("📋 Lista Borrador")
    
    canciones_disponibles = [datos["titulo_real"] for datos in cancionero.values()]
    cancion_a_añadir = st.selectbox("Añadir canción al borrador:", ["-- Seleccionar --"] + canciones_disponibles)
    
    if st.button("➕ Añadir borrador") and cancion_a_añadir != "-- Seleccionar --":
        if cancion_a_añadir not in st.session_state.lista_servicio:
            st.session_state.lista_servicio.append(cancion_a_añadir)
            st.success(f"¡{cancion_a_añadir} añadida!")
        else:
            st.warning("Esta canción ya está en tu borrador.")
            
    st.write("---")
    
    if st.session_state.lista_servicio:
        st.write("**Seleccionadas:**")
        for i, cancion in enumerate(st.session_state.lista_servicio, 1):
            st.write(f"**{i}. {cancion}**")
            
        if st.button("🗑️ Limpiar borrador"):
            st.session_state.lista_servicio = []
            st.rerun()

# ==========================================
# PESTAÑAS PRINCIPALES
# ==========================================
pestana_buscar, pestana_calendario, pestana_agregar = st.tabs([
    "🔍 Buscar Canciones", 
    "📅 Calendario de Servicios", 
    "➕ Agregar Canción"
])

# --- PESTAÑA 1: BUSCADOR ---
with pestana_buscar:
    busqueda = st.text_input("🔍 Busca por nombre de canción o palabra clave:", "")
    busqueda_limpia = busqueda.lower().strip()

    clave_seleccionada = None

    if busqueda_limpia:
        coincidencias = [c for c in cancionero.keys() if busqueda_limpia in c]
                
        if len(coincidencias) == 0:
            st.error("❌ No se encontró ninguna canción con ese nombre.")
        elif len(coincidencias) == 1:
            clave_seleccionada = coincidencias[0]
        else:
            st.warning("🔍 Varias opciones encontradas. Elige una:")
            opciones_pantalla = {cancionero[c]["titulo_real"]: c for c in coincidencias}
            seleccion = st.selectbox("Elige la canción:", list(opciones_pantalla.keys()))
            clave_seleccionada = opciones_pantalla[seleccion]
            
        if clave_seleccionada:
            cancion = cancionero[clave_seleccionada]
            st.subheader(f"🎵 {cancion['titulo_real']}")
            
            with st.expander("🛠️ Opciones de edición / eliminar"):
                nuevos_acordes_editados = st.text_area(
                    "Editar acordes:", 
                    value=cancion['acordes'], 
                    height=150,
                    key=f"edit_{clave_seleccionada}"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Guardar Cambios", key=f"btn_save_{clave_seleccionada}"):
                        cancionero[clave_seleccionada]['acordes'] = nuevos_acordes_editados.strip()
                        db["canciones"] = cancionero
                        guardar_datos(db)
                        st.success("¡Canción editada!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Eliminar", key=f"btn_del_{clave_seleccionada}"):
                        del cancionero[clave_seleccionada]
                        db["canciones"] = cancionero
                        guardar_datos(db)
                        st.success("¡Eliminada!")
                        st.rerun()
            
            st.code(cancion['acordes'], language="text")
    else:
        st.info("Escribe arriba para buscar acordes o ve al Calendario para ver las canciones del próximo servicio.")

# --- PESTAÑA 2: CALENDARIO DE SERVICIOS ---
with pestana_calendario:
    st.subheader("📅 Agenda de Servicios y Alabanzas")
    
    opcion_cal = st.radio("¿Qué deseas hacer?", ["Ver Agenda de Servicios", "Programar Nuevo Servicio ➕"])
    
    if opcion_cal == "Programar Nuevo Servicio ➕":
        st.markdown("### 📝 Programar un Servicio")
        fecha_servicio = st.date_input("Fecha del Servicio:", datetime.now())
        tipo_servicio = st.selectbox("Tipo de Servicio / Reunión:", ["Servicio Dominical", "Reunión de Jóvenes", "Servicio de Oración", "Especial / Evento"])
        
        st.write("**Selecciona las canciones para este día:**")
        canciones_para_fecha = st.multiselect(
            "Escribe o selecciona las canciones:",
            canciones_disponibles,
            default=st.session_state.lista_servicio if st.session_state.lista_servicio else []
        )
        
        notas_adicionales = st.text_input("Indicaciones especiales (Ej: Tocar en tono Sol, ensayo a las 4 PM):")
        
        if st.button("💾 Guardar en la Agenda"):
            if canciones_para_fecha:
                fecha_str = fecha_servicio.strftime("%Y-%m-%d")
                
                db["calendario"][fecha_str] = {
                    "tipo": tipo_servicio,
                    "canciones": canciones_para_fecha,
                    "notas": notas_adicionales
                }
                guardar_datos(db)
                st.success(f"¡Servicio para el {fecha_str} guardado con éxito!")
                st.session_state.lista_servicio = [] # Limpiamos borrador
                st.rerun()
            else:
                st.error("Selecciona al menos una canción para programar el servicio.")

    elif opcion_cal == "Ver Agenda de Servicios":
        if not calendario:
            st.info("Aún no hay servicios programados en la agenda. ¡Programa el primero!")
        else:
            fechas_ordenadas = sorted(calendario.keys(), reverse=False)
            
            # Selector de fecha programada
            fechas_formateadas = {datetime.strptime(f, "%Y-%m-%d").strftime("%d/%m/%Y") + f" - {calendario[f]['tipo']}": f for f in fechas_ordenadas}
            
            seleccion_fecha_label = st.selectbox("Elige la fecha del servicio a consultar:", list(fechas_formateadas.keys()))
            clave_fecha = fechas_formateadas[seleccion_fecha_label]
            
            info_servicio = calendario[clave_fecha]
            
            st.markdown(f"### 🎼 Repertorio: {info_servicio['tipo']}")
            if info_servicio['notas']:
                st.info(f"📌 **Nota:** {info_servicio['notas']}")
                
            st.write("---")
            
            # Desplegar los acordes de las canciones de esa fecha
            for i, nombre_c in enumerate(info_servicio['canciones'], 1):
                # Buscamos los acordes
                acordes_c = "Acordes no encontrados"
                for c_item in cancionero.values():
                    if c_item["titulo_real"] == nombre_c:
                        acordes_c = c_item["acordes"]
                        break
                        
                with st.expander(f"🎵 {i}. {nombre_c}", expanded=True):
                    st.code(acordes_c, language="text")
                    
            if st.button("🗑️ Eliminar este servicio de la agenda"):
                del db["calendario"][clave_fecha]
                guardar_datos(db)
                st.success("Servicio eliminado de la agenda.")
                st.rerun()

# --- PESTAÑA 3: AGREGAR CANCIÓN ---
with pestana_agregar:
    st.subheader("📝 Registra una nueva canción")
    metodo = st.radio("Elige cómo deseas agregarla:", ["Escribir manualmente", "Tomar una foto / Cargar Imagen 📸"])
    
    if metodo == "Escribir manualmente":
        nuevo_titulo = st.text_input("Nombre de la canción (Ej: Cuan grande es el):")
        nuevos_acordes = st.text_area("Estructura y acordes:", placeholder="Estrofa // G C D //\nCoro // G C D //")
        
        if st.button("💾 Guardar Canción"):
            if nuevo_titulo and nuevos_acordes:
                clave_nueva = nuevo_titulo.lower().strip().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
                
                cancionero[clave_nueva] = {
                    "titulo_real": nuevo_titulo.strip(),
                    "acordes": nuevos_acordes.strip()
                }
                db["canciones"] = cancionero
                guardar_datos(db)
                st.success(f"¡{nuevo_titulo} guardada!")
                st.rerun()
            else:
                st.error("Por favor completa el título y los acordes.")
                
    elif metodo == "Tomar una foto / Cargar Imagen 📸":
        if API_KEY_GEMINI == "AQUÍ_PEGA_TU_CLAVE":
            st.warning("⚠️ Configura tu API Key.")
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
                            instrucciones = """
                            Analiza la imagen de este cuaderno de acordes musicales. 
                            Extrae el título de la canción y los acordes correspondientes a cada sección (Estrofa, Pre coro, Coro).
                            Debes estructurar el resultado EXACTAMENTE con el siguiente formato, usando barras dobles '//':
                            
                            Título: Nombre de la Canción
                            ---
                            Estrofa // D A D, Bm A D //
                            Coro // D Bm G A //
                            
                            No agregues letras ni explicaciones. Es muy importante que uses la palabra 'Estrofa' y NUNCA 'Estropa'.
                            """
                            
                            respuesta = model.generate_content([instrucciones, imagen_procesada])
                            resultado_texto = respuesta.text
                            
                            lineas = resultado_texto.strip().split("\n")
                            titulo_detectado = ""
                            acordes_detectados = []
                            encontró_separador = False
                            
                            for linea in lineas:
                                linea_limpia = linea.strip()
                                if not linea_limpia:
                                    continue
                                if (linea_limpia.lower().startswith("titulo:") or linea_limpia.lower().startswith("título:")) and not titulo_detectado:
                                    titulo_detectado = linea.split(":", 1)[1].strip()
                                    continue
                                if "---" in linea_limpia:
                                    encontró_separador = True
                                    continue
                                if encontró_separador or (titulo_detectado and not linea_limpia.lower().startswith("titulo")):
                                    acordes_detectados.append(linea)
                            
                            if not titulo_detectado:
                                titulo_detectado = "Nueva Canción Detectada"
                            
                            acordes_final_texto = "\n".join(acordes_detectados) if acordes_detectados else resultado_texto
                                
                            st.session_state["temp_titulo"] = titulo_detectado
                            st.session_state["temp_acordes"] = acordes_final_texto.strip()
                            st.rerun()
                            
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
                    db["canciones"] = cancionero
                    guardar_datos(db)
                    
                    st.success(f"¡{titulo_final} ha sido guardada!")
                    del st.session_state["temp_titulo"]
                    del st.session_state["temp_acordes"]
                    st.rerun()