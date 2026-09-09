from datetime import datetime
from difflib import get_close_matches
import json
import re
import urllib.parse
from PIL import Image
import requests
import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS ENFOCADOS EN iOS 18
st.set_page_config(
    page_title="Libres por Cristo",
    page_icon="🎹",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Estilos CSS iOS 18 + Glassmorphism + Ocultamiento de la interfaz Streamlit
st.markdown(
    """
    <style>
    /* Ocultar interfaz nativa de Streamlit para apariencia de App Nativa */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* Reducir espacio superior vacante */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* Fondo principal modo oscuro iOS 18 */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #090d16 0%, #111827 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
        color: #f8fafc;
    }

    /* Tarjetas estilo Glassmorphism de iOS 18 */
    .ios-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    /* Línea divisora sutil y elegante estilo iOS */
    .ios-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, rgba(56, 189, 248, 0.4) 50%, rgba(255, 255, 255, 0) 100%);
        margin: 18px 0;
        border: none;
    }

    /* Cajas de código con estética minimalista */
    div[data-testid="stCodeBlock"] {
        background-color: rgba(2, 6, 23, 0.7) !important;
        border-left: 4px solid #38bdf8 !important;
        border-radius: 12px !important;
    }

    /* Botones Táctiles estilo iOS 18 */
    div.stButton > button {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-radius: 14px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25);
        width: 100%;
    }

    div.stButton > button:hover {
        transform: scale(0.98);
        background-color: #0369a1 !important;
    }

    /* Cajas de texto e inputs estilo iOS 18 */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: white !important;
    }

    /* Tabs / Segmented Control estilo iOS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 4px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-radius: 12px;
    }

    /* Badges visuales con colores 100% distintivos */
    .badge-tono { background-color: #0284c7; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 15px; display: inline-block; margin-bottom: 15px; border: 1px solid #38bdf8; }
    .badge-intro { background-color: #0f766e; color: #99f6e4; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #14b8a6; }
    .badge-estrofa { background-color: #15803d; color: #bbf7d0; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #22c55e; }
    .badge-coro { background-color: #b45309; color: #fef08a; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #eab308; }
    .badge-precoro { background-color: #7e22ce; color: #e9d5ff; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #a855f7; }
    .badge-puente { background-color: #0284c7; color: #bae6fd; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #38bdf8; }
    .badge-default { background-color: #334155; color: #cbd5e1; padding: 4px 8px; border-radius: 6px; font-weight: bold; }

    /* Contador en sidebar */
    .counter-badge {
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 2. CONFIGURACIÓN DE BASE DE DATOS Y CLAVES
BIN_ID = st.secrets.get("BIN_ID", "6a5f89cada38895dfe7b600f")
MASTER_KEY = st.secrets.get(
    "MASTER_KEY", "$2a$10$vknOXY8VuZW.tNRDuxItD.5YSkYK1V8hGisTCx56w3VwGCUDLLw0i"
)
OCR_KEY = st.secrets.get("OCR_KEY", "K87431578588957")

URL_JSONBIN = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"Content-Type": "application/json", "X-Master-Key": MASTER_KEY}


# 3. FUNCIONES EN LA NUBE
@st.cache_data(ttl=5)
def cargar_datos_nube():
    try:
        respuesta = requests.get(URL_JSONBIN, headers=HEADERS)
        if respuesta.status_code == 200:
            return respuesta.json()["record"]
        else:
            st.error("Error al conectar con la base de datos en la nube.")
            return {"canciones": {}, "calendario": {}}
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return {"canciones": {}, "calendario": {}}


def guardar_datos_nube(datos):
    try:
        respuesta = requests.put(URL_JSONBIN, json=datos, headers=HEADERS)
        if respuesta.status_code == 200:
            st.cache_data.clear()
            return True
        else:
            st.error("No se pudieron guardar los datos en la nube.")
            return False
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False


# 4. LÓGICA DE TRANSPOSICIÓN Y DETECCIÓN DE TONO
NOTAS_CROMATICAS = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]
NOTAS_EQUIVALENTES = {
    "Db": "C#",
    "Eb": "D#",
    "Fb": "E",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "Cb": "B",
}


def transponer_acorde(acorde, semitonos):
    def transponer_nota(m):
        nota = m.group(1)
        if nota in NOTAS_EQUIVALENTES:
            nota = NOTAS_EQUIVALENTES[nota]
        if nota in NOTAS_CROMATICAS:
            idx = (NOTAS_CROMATICAS.index(nota) + semitonos) % 12
            return NOTAS_CROMATICAS[idx]
        return nota

    patron = r"([A-G][#b]?)"
    return re.sub(patron, transponer_nota, acorde)


def transponer_texto_acordes(texto, semitonos):
    if semitonos == 0:
        return texto
    lineas = texto.split("\n")
    lineas_transp = []

    for linea in lineas:
        if "//" in linea:
            partes = linea.split("//")
            nombre_sec = partes[0]
            acordes_sec = partes[1] if len(partes) > 1 else ""
            resto = "//".join(partes[2:]) if len(partes) > 2 else ""

            acordes_transp = transponer_acorde(acordes_sec, semitonos)

            linea_reconstruida = f"{nombre_sec}//{acordes_transp}//"
            if resto:
                linea_reconstruida += f"{resto}"
            lineas_transp.append(linea_reconstruida)
        else:
            palabras = linea.split()
            if palabras and sum(
                1 for p in palabras if re.match(r"^[A-G][#b]?", p)
            ) >= len(palabras) * 0.4:
                lineas_transp.append(transponer_acorde(linea, semitonos))
            else:
                lineas_transp.append(linea)

    return "\n".join(lineas_transp)


def detectar_tono_principal(texto_acordes):
    patron_acorde = (
        r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add)?[0-9]?(?:\/[A-G][#b]?)?\b"
    )
    acordes = re.findall(patron_acorde, texto_acordes)
    if acordes:
        return acordes[0]
    return "N/A"


def renderizar_bloques_color(texto_acordes):
    tono_detectado = detectar_tono_principal(texto_acordes)

    st.markdown(
        f'<div class="badge-tono">🎵 Tonalidad actual: {tono_detectado}</div>',
        unsafe_allow_html=True,
    )

    lineas = texto_acordes.split("\n")

    for linea in lineas:
        if "//" in linea:
            partes = linea.split("//")
            nombre_sec = partes[0].strip()
            acordes_sec = partes[1].strip() if len(partes) > 1 else ""

            sec_lower = nombre_sec.lower()
            clase_badge = "badge-default"
            if "intro" in sec_lower:
                clase_badge = "badge-intro"
            elif (
                "estrofa" in sec_lower or "verso" in sec_lower or "est" in sec_lower
            ):
                clase_badge = "badge-estrofa"
            elif "pre" in sec_lower:
                clase_badge = "badge-precoro"
            elif "coro" in sec_lower or "refrão" in sec_lower:
                clase_badge = "badge-coro"
            elif "puente" in sec_lower or "ponte" in sec_lower:
                clase_badge = "badge-puente"

            html_tarjeta = (
                f'<div style="margin-bottom: 12px; background: rgba(2, 6, 23, 0.6); padding:'
                f' 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);"><span'
                f' class="{clase_badge}">{nombre_sec}</span><p'
                ' style="font-family: monospace; font-size: 18px; color:'
                ' #38bdf8; margin: 8px 0 0 0; font-weight: bold; letter-spacing:'
                f' 1px;">{acordes_sec}</p></div>'
            )
            st.markdown(html_tarjeta, unsafe_allow_html=True)
        else:
            if linea.strip():
                st.markdown(
                    f"<p style='font-family: monospace; font-size:"
                    f" 16px;'>{linea}</p>",
                    unsafe_allow_html=True,
                )


# Carga Inicial de Datos desde JSONBin
db = cargar_datos_nube()
cancionero = db.get("canciones", {})
calendario = db.get("calendario", {})

if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []

# Encabezado estilo iOS 18
st.markdown(
    """
    <div class="ios-card" style="text-align: center; padding: 15px;">
        <h1 style='color: #ffffff; margin: 0; font-size: 28px;'>🎹 Libres por Cristo</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# BARRA LATERAL
with st.sidebar:
    cnt = len(st.session_state.lista_servicio)
    st.markdown(
        f"### 📋 Lista Borrador <span class='counter-badge'>{cnt}</span>",
        unsafe_allow_html=True,
    )

    canciones_disponibles = sorted(
        [datos["titulo_real"] for datos in cancionero.values() if "titulo_real" in datos]
    )

    cancion_a_añadir = st.selectbox(
        "Añadir canción al borrador:",
        ["-- Seleccionar --"] + canciones_disponibles,
    )

    if (
        st.button("➕ Agregar canción")
        and cancion_a_añadir != "-- Seleccionar --"
    ):
        if cancion_a_añadir not in st.session_state.lista_servicio:
            st.session_state.lista_servicio.append(cancion_a_añadir)
            st.rerun()
        else:
            st.warning("Ya está en tu borrador.")

    st.markdown('<hr class="ios-divider">', unsafe_allow_html=True)

    if st.session_state.lista_servicio:
        st.write("**Orden de ejecución:**")

        for i, cancion_nom in enumerate(st.session_state.lista_servicio):
            tono_str = ""
            for item in cancionero.values():
                if item.get("titulo_real") == cancion_nom:
                    tono_str = f"({detectar_tono_principal(item.get('acordes', ''))})"
                    break

            c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
            with c1:
                st.markdown(
                    f"<p style='margin:0; font-size:13px;'><b>{i+1}. {cancion_nom}</b> <span style='color:#38bdf8;'>{tono_str}</span></p>",
                    unsafe_allow_html=True,
                )
            with c2:
                if i > 0 and st.button("▲", key=f"up_{i}"):
                    st.session_state.lista_servicio[i], (
                        st.session_state.lista_servicio[i - 1]
                    ) = (
                        st.session_state.lista_servicio[i - 1],
                        st.session_state.lista_servicio[i],
                    )
                    st.rerun()
            with c3:
                if (
                    i < len(st.session_state.lista_servicio) - 1
                    and st.button("▼", key=f"down_{i}")
                ):
                    st.session_state.lista_servicio[i], (
                        st.session_state.lista_servicio[i + 1]
                    ) = (
                        st.session_state.lista_servicio[i + 1],
                        st.session_state.lista_servicio[i],
                    )
                    st.rerun()
            with c4:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.lista_servicio.pop(i)
                    st.rerun()

        st.markdown('<hr class="ios-divider">', unsafe_allow_html=True)

        texto_borrador = "*REPERTORIO PROPUESTO*\n\n"
        for idx, nom in enumerate(st.session_state.lista_servicio, 1):
            texto_borrador += f"{idx}. {nom}\n"

        url_borrador_wa = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_borrador)}"
        st.markdown(
            f"[📲 Enviar borrador a WhatsApp]({url_borrador_wa})",
            unsafe_allow_html=True,
        )

        if st.button("🗑️ Vaciar borrador"):
            st.session_state.lista_servicio = []
            st.rerun()
    else:
        st.info("El borrador está vacío. Agrega canciones para armar el orden.")

# PESTAÑAS PRINCIPALES
pestana_buscar, pestana_calendario, pestana_agregar = st.tabs([
    "🔍 Buscar Canciones",
    "📅 Calendario de Servicios",
    "➕ Agregar Canción",
])

# --- PESTAÑA 1: BUSCADOR ---
with pestana_buscar:
    st.subheader("🔍 Buscador de Canciones")

    titulos_reales = sorted(
        [v["titulo_real"] for v in cancionero.values() if "titulo_real" in v]
    )

    if titulos_reales:
        cancion_seleccionada = st.selectbox(
            "Escribe el nombre de la canción:",
            options=titulos_reales,
            index=0,
            key="select_cancion_unica",
        )

        st.markdown('<hr class="ios-divider">', unsafe_allow_html=True)

        clave_sel = next(
            (
                k
                for k, v in cancionero.items()
                if v["titulo_real"] == cancion_seleccionada
            ),
            None,
        )

        if clave_sel:
            cancion = cancionero[clave_sel]

            st.markdown(f"## 🎵 {cancion['titulo_real']}")

            semitonos_v = st.slider(
                "Transponer tono en vivo (Semitonos):", -6, 6, 0
            )
            acordes_mostrados = transponer_texto_acordes(
                cancion["acordes"], semitonos_v
            )

            renderizar_bloques_color(acordes_mostrados)

            with st.expander("🛠️ Editar datos o acordes"):
                edit_titulo = st.text_input(
                    "Título:", value=cancion["titulo_real"]
                )
                edit_acordes = st.text_area(
                    "Acordes:", value=cancion["acordes"], height=150
                )

                col_s, col_d = st.columns(2)
                with col_s:
                    if st.button("💾 Guardar Cambios"):
                        cancionero[clave_sel]["titulo_real"] = (
                            edit_titulo.strip()
                        )
                        cancionero[clave_sel]["acordes"] = edit_acordes.strip()
                        db["canciones"] = cancionero
                        if guardar_datos_nube(db):
                            st.success("¡Canción actualizada!")
                            st.rerun()
                with col_d:
                    if st.button("🗑️ Eliminar Canción"):
                        del cancionero[clave_sel]
                        db["canciones"] = cancionero
                        if guardar_datos_nube(db):
                            st.success("Canción eliminada.")
                            st.rerun()
    else:
        st.info("No hay canciones disponibles en el cancionero.")

# --- PESTAÑA 2: CALENDARIO DE SERVICIOS Y MODO EN VIVO ---
with pestana_calendario:
    opcion_cal = st.radio(
        "Modalidad:",
        ["Ver Agenda de Servicios", "Programar Nuevo Servicio ➕"],
        horizontal=True,
    )

    if opcion_cal == "Programar Nuevo Servicio ➕":
        st.markdown("### 📝 Programar un Servicio")
        fecha_servicio = st.date_input("Fecha:", datetime.now())
        tipo_servicio = st.selectbox(
            "Evento:",
            [
                "Servicio Dominical",
                "Reunión de Jóvenes",
                "Servicio de Oración",
                "Especial / Evento",
            ],
        )

        canciones_para_fecha = st.multiselect(
            "Selecciona el repertorio:",
            canciones_disponibles,
            default=st.session_state.lista_servicio,
        )
        notas_adicionales = st.text_input(
            "Observaciones (Ej: Tocar en Sol, Ensayo 4 PM):"
        )

        if st.button("💾 Guardar en Agenda"):
            if canciones_para_fecha:
                fecha_str = fecha_servicio.strftime("%Y-%m-%d")
                db["calendario"][fecha_str] = {
                    "tipo": tipo_servicio,
                    "canciones": canciones_para_fecha,
                    "notas": notas_adicionales,
                }
                if guardar_datos_nube(db):
                    st.success("¡Servicio agendado!")
                    st.session_state.lista_servicio = []
                    st.rerun()

    elif opcion_cal == "Ver Agenda de Servicios":
        if not calendario:
            st.info("No hay servicios agendados aún.")
        else:
            fechas_ordenadas = sorted(calendario.keys())
            fechas_formateadas = {
                datetime.strptime(f, "%Y-%m-%d").strftime("%d/%m/%Y")
                + f" - {calendario[f]['tipo']}": f
                for f in fechas_ordenadas
            }

            seleccion_fecha_label = st.selectbox(
                "Selecciona una fecha:", list(fechas_formateadas.keys())
            )
            clave_fecha = fechas_formateadas[seleccion_fecha_label]
            info_servicio = calendario[clave_fecha]

            st.markdown(f"### 🎼 Repertorio: {info_servicio['tipo']}")
            if info_servicio["notas"]:
                st.info(f"📌 **Observación:** {info_servicio['notas']}")

            texto_wa = (
                f"*REPERTORIO {info_servicio['tipo'].upper()}*\n📅"
                f" *Fecha:* {clave_fecha}\n\n"
            )
            for idx, c_nom in enumerate(info_servicio["canciones"], 1):
                texto_wa += f"{idx}. {c_nom}\n"

            if info_servicio["notas"]:
                texto_wa += f"\n📌 *Notas:* {info_servicio['notas']}"

            url_wa = (
                f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_wa)}"
            )
            st.markdown(
                f"[📲 Compartir Repertorio en WhatsApp]({url_wa})",
                unsafe_allow_html=True,
            )

            if st.checkbox("🚀 MODO EN VIVO (Lectura Gigante para Servicio)"):
                cancion_idx = st.slider(
                    "Cambiar de canción:",
                    1,
                    len(info_servicio["canciones"]),
                    1,
                )
                nombre_c = info_servicio["canciones"][cancion_idx - 1]

                acordes_c = "Sin acordes"
                for c_item in cancionero.values():
                    if c_item.get("titulo_real") == nombre_c:
                        acordes_c = c_item["acordes"]
                        break

                st.markdown(
                    f"<h2 style='text-align: center; color: #38bdf8;'>{cancion_idx}. {nombre_c}</h2>",
                    unsafe_allow_html=True,
                )

                renderizar_bloques_color(acordes_c)

            else:
                for i, nombre_c in enumerate(info_servicio["canciones"], 1):
                    acordes_c = "Acordes no registrados"
                    for c_item in cancionero.values():
                        if c_item.get("titulo_real") == nombre_c:
                            acordes_c = c_item["acordes"]
                            break
                    with st.expander(f"🎵 {i}. {nombre_c}", expanded=True):
                        renderizar_bloques_color(acordes_c)

            if st.button("🗑️ Eliminar este servicio"):
                del db["calendario"][clave_fecha]
                if guardar_datos_nube(db):
                    st.success("Servicio eliminado.")
                    st.rerun()

# --- PESTAÑA 3: AGREGAR CANCIÓN ---
with pestana_agregar:
    metodo = st.radio(
        "Fuente de origen:",
        [
            "Escribir manualmente",
            "Pegar Link Directo de Cifra Club 🎸",
            "Tomar una foto / Cargar Imagen 📸",
        ],
    )

    if metodo == "Escribir manualmente":
        nuevo_titulo = st.text_input("Título de la canción:")
        nuevos_acordes = st.text_area(
            "Estructura y acordes:",
            placeholder="Intro // G D //\nEstrofa // G C D //",
        )

        if st.button("💾 Guardar Canción"):
            if nuevo_titulo and nuevos_acordes:
                clave_nueva = (
                    nuevo_titulo.lower()
                    .strip()
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                )
                cancionero[clave_nueva] = {
                    "titulo_real": nuevo_titulo.strip(),
                    "acordes": nuevos_acordes.strip(),
                }
                db["canciones"] = cancionero
                if guardar_datos_nube(db):
                    st.success("¡Canción guardada!")
                    st.rerun()

    elif metodo == "Pegar Link Directo de Cifra Club 🎸":
        url_directa = st.text_input(
            "Link de Cifra Club:",
            placeholder="https://www.cifraclub.com/marcos-witt/cuan-grande-es-el/",
        )

        if st.button("📥 Importar desde Cifra Club"):
            if url_directa:
                st.session_state["url_cifra_seleccionada"] = url_directa
            else:
                st.error("Ingresa una URL válida.")

        if "url_cifra_seleccionada" in st.session_state:
            st.write("---")
            semitonos_dict = {
                "Tono Original": 0,
                "+1 Semitono": 1,
                "+2 Semitonos": 2,
                "+3 Semitonos": 3,
                "-1 Semitono": -1,
                "-2 Semitonos": -2,
            }
            opcion_trans = st.selectbox(
                "Transposición:", list(semitonos_dict.keys())
            )
            semitonos = semitonos_dict[opcion_trans]

            if st.button("✨ Extraer y Procesar Estructura"):
                with st.spinner("Analizando bloques y acordes..."):
                    try:
                        from bs4 import BeautifulSoup

                        res = requests.get(
                            st.session_state["url_cifra_seleccionada"],
                            headers={
                                "User-Agent": (
                                    "Mozilla/5.0 (Windows NT 10.0; Win64;"
                                    " x64) Chrome/120.0.0.0 Safari/537.36"
                                )
                            },
                        )
                        soup = BeautifulSoup(res.text, "html.parser")

                        titulo_elem = soup.find("h1", class_="t1") or soup.find(
                            "h1"
                        )
                        titulo_real = (
                            titulo_elem.get_text(strip=True)
                            if titulo_elem
                            else "Nueva Canción"
                        )

                        texto_resumido = parsear_acordes_cifra(soup)

                        if texto_resumido:
                            texto_transp = transponer_texto_acordes(
                                texto_resumido, semitonos
                            )
                            st.session_state["temp_titulo"] = titulo_real
                            st.session_state["temp_acordes"] = texto_transp
                            st.success("¡Estructura extraída exitosamente!")
                            del st.session_state["url_cifra_seleccionada"]
                            st.rerun()
                        else:
                            st.error(
                                "No se pudo identificar la estructura de la"
                                " canción."
                            )
                    except Exception as e:
                        st.error(f"Error al procesar la URL: {e}")

    elif metodo == "Tomar una foto / Cargar Imagen 📸":
        foto = st.file_uploader(
            "Cargar imagen de la partitura / cifrado:",
            type=["jpg", "jpeg", "png"],
        )
        if foto is not None:
            st.image(Image.open(foto), caption="Imagen cargada", width=250)
            if st.button("🪄 Digitalizar con OCR"):
                with st.spinner("Escaneando texto..."):
                    try:
                        foto.seek(0)
                        files = {
                            "file": (foto.name, foto.getvalue(), foto.type)
                        }
                        payload = {
                            "apikey": OCR_KEY,
                            "language": "spa",
                            "OCREngine": "2",
                        }
                        respuesta = requests.post(
                            "https://api.ocr.space/parse/image",
                            files=files,
                            data=payload,
                            timeout=20,
                        )
                        resultado = respuesta.json()

                        if (
                            resultado.get("OCRExitCode") == 1
                            and resultado.get("ParsedResults")
                        ):
                            texto = resultado["ParsedResults"][0].get(
                                "ParsedText", ""
                            )
                            lineas = [
                                l.strip() for l in texto.split("\n") if l.strip()
                            ]
                            st.session_state["temp_titulo"] = (
                                lineas[0] if lineas else "Nueva Canción"
                            )
                            st.session_state["temp_acordes"] = "\n".join(
                                lineas[1:]
                            )
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error en OCR: {e}")

    # Bloque de Confirmación y Guardado
    if "temp_titulo" in st.session_state:
        st.subheader("🔍 Confirmación Final:")
        titulo_f = st.text_input(
            "Título:", value=st.session_state["temp_titulo"]
        )
        acordes_f = st.text_area(
            "Acordes Extraídos:",
            value=st.session_state["temp_acordes"],
            height=200,
        )

        if st.button("💾 Guardar Definitivamente"):
            clave_nueva = (
                titulo_f.lower()
                .strip()
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            cancionero[clave_nueva] = {
                "titulo_real": titulo_f.strip(),
                "acordes": acordes_f.strip(),
            }
            db["canciones"] = cancionero
            if guardar_datos_nube(db):
                st.success("¡Canción guardada con éxito!")
                del st.session_state["temp_titulo"]
                del st.session_state["temp_acordes"]
                st.rerun()
