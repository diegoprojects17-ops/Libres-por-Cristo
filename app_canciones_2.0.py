from datetime import datetime
from difflib import get_close_matches
import json
import re
import urllib.parse
from PIL import Image
import requests
import streamlit as st

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS LIQUID GLASS
st.set_page_config(
    page_title="Libres por Cristo - iOS 18", page_icon="🎹", layout="centered"
)

# Estilos CSS iOS 18 Liquid Glass
st.markdown(
    """
    <style>
    /* Fondo principal fluido e hiper-minimalista */
    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 0%, #1f2937 0%, #0b0f17 100%) !important;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", sans-serif;
        color: #f3f4f6;
    }

    /* Tarjetas Liquid Glass */
    .ios-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(25px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(25px) saturate(180%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 22px !important;
        padding: 22px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }

    /* Línea divisora estilo cristal */
    .ios-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0.25) 50%, rgba(255, 255, 255, 0) 100%);
        margin: 20px 0;
        border: none;
    }

    /* Cajas de código con textura de cristal oscuro */
    div[data-testid="stCodeBlock"] {
        background: rgba(15, 23, 42, 0.6) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-left: 4px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 14px !important;
    }

    /* Botones Táctiles Liquid Glass */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.35) !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        width: 100%;
    }

    div.stButton > button:hover {
        transform: translateY(-1px) scale(0.99);
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 6px 20px rgba(255, 255, 255, 0.1);
    }

    /* Entradas e Inputs estilo cristal */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
    }

    /* Tabs / Control segmentado transparente */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(15px);
        border-radius: 18px;
        padding: 5px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        color: #ffffff !important;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    /* Badges visuales */
    .badge-tono { 
        background: rgba(255, 255, 255, 0.12); 
        color: #ffffff; 
        padding: 6px 14px; 
        border-radius: 20px; 
        font-weight: bold; 
        font-size: 15px; 
        display: inline-block; 
        margin-bottom: 15px; 
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(8px);
    }
    
    .badge-intro { background-color: rgba(20, 184, 166, 0.2); color: #99f6e4; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid rgba(20, 184, 166, 0.4); }
    .badge-estrofa { background-color: rgba(34, 197, 94, 0.2); color: #bbf7d0; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid rgba(34, 197, 94, 0.4); }
    .badge-coro { background-color: rgba(234, 179, 8, 0.2); color: #fef08a; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid rgba(234, 179, 8, 0.4); }
    .badge-precoro { background-color: rgba(168, 85, 247, 0.2); color: #e9d5ff; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid rgba(168, 85, 247, 0.4); }
    
    .badge-puente { 
        background-color: rgba(59, 130, 246, 0.25); 
        color: #93c5fd; 
        padding: 4px 8px; 
        border-radius: 6px; 
        font-weight: bold; 
        border: 1px solid rgba(59, 130, 246, 0.5); 
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.2);
    }

    .badge-default { background-color: rgba(255, 255, 255, 0.08); color: #e5e7eb; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid rgba(255, 255, 255, 0.15); }

    .counter-badge {
        background: rgba(255, 255, 255, 0.2);
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 14px;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.3);
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


# 3. FUNCIONES EN LA NUBE Y ENUMERACIÓN AUTOMÁTICA
@st.cache_data(ttl=5)
def cargar_datos_nube():
    try:
        respuesta = requests.get(URL_JSONBIN, headers=HEADERS)
        if respuesta.status_code == 200:
            record = respuesta.json()["record"]
            if "canciones" not in record:
                record["canciones"] = {}
            if "calendario" not in record:
                record["calendario"] = {}

            # PROCESO DE ENUMERACIÓN DE CANCIONES EXISTENTES EN JSONBIN
            canciones = record["canciones"]
            hubo_cambios = False
            i = 1
            nuevas_canciones = {}

            for clave, datos in canciones.items():
                titulo_actual = datos.get("titulo_real", "")
                # Si el título no empieza con un número y punto (ej. "1. "), se le asigna
                if not re.match(r"^\d+\.\s", titulo_actual):
                    titulo_limpio = re.sub(r"^\d+\.\s*", "", titulo_actual)
                    nuevo_titulo = f"{i}. {titulo_limpio}"
                    datos["titulo_real"] = nuevo_titulo
                    hubo_cambios = True
                else:
                    # Garantizar que lleve el correlativo consecutivo
                    titulo_limpio = re.sub(r"^\d+\.\s*", "", titulo_actual)
                    nuevo_titulo = f"{i}. {titulo_limpio}"
                    if nuevo_titulo != titulo_actual:
                        datos["titulo_real"] = nuevo_titulo
                        hubo_cambios = True

                nuevas_canciones[clave] = datos
                i += 1

            if hubo_cambios:
                record["canciones"] = nuevas_canciones
                guardar_datos_nube(record)

            return record
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


def formatear_titulo_con_numero(titulo_bruto, total_existentes):
    """Limpia cualquier número previo y antepone el correlativo según la cantidad actual."""
    titulo_limpio = re.sub(r"^\d+\.\s*", "", titulo_bruto.strip())
    numero_nuevo = total_existentes + 1
    return f"{numero_nuevo}. {titulo_limpio}"


# 4. FUNCIONES DE TRANSPOSICIÓN Y DETECCIÓN
NOTAS_CROMATICAS = [
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
]
NOTAS_EQUIVALENTES = {
    "Db": "C#", "Eb": "D#", "Fb": "E", "Gb": "F#", "Ab": "G#", "Bb": "A#", "Cb": "B"
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
                f'<div style="margin-bottom: 12px; background: rgba(255, 255, 255, 0.03); padding:'
                f' 14px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.08);'
                f' backdrop-filter: blur(10px);"><span class="{clase_badge}">{nombre_sec}</span><p'
                ' style="font-family: monospace; font-size: 18px; color:'
                ' #ffffff; margin: 10px 0 0 0; font-weight: bold; letter-spacing:'
                f' 1px;">{acordes_sec}</p></div>'
            )
            st.markdown(html_tarjeta, unsafe_allow_html=True)
        else:
            if linea.strip():
                st.markdown(
                    f"<p style='font-family: monospace; font-size:"
                    f" 16px; color: #e5e7eb;'>{linea}</p>",
                    unsafe_allow_html=True,
                )


# Carga Inicial de Datos desde JSONBin
db = cargar_datos_nube()
cancionero = db.get("canciones", {})
calendario = db.get("calendario", {})

if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []

# Encabezado estilo Liquid Glass
st.markdown(
    """
    <div class="ios-card" style="text-align: center; padding: 18px;">
        <h1 style='color: #ffffff; margin: 0; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;'>🎹 Libres por Cristo</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- BARRA LATERAL (LISTA BORRADOR) ---
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
                    f"<p style='margin:0; font-size:13px;'><b>{i+1}. {cancion_nom}</b> <span style='color:#e2e8f0;'>{tono_str}</span></p>",
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

# --- PESTAÑA 2: CALENDARIO DE SERVICIOS ---
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
                    f"<h2 style='text-align: center; color: #ffffff;'>{cancion_idx}. {nombre_c}</h2>",
                    unsafe_allow_html=True,
                )

                st_sem = st.number_input(
                    "Transponer tono (Semitonos):",
                    min_value=-6,
                    max_value=6,
                    value=0,
                    step=1,
                    key=f"trans_vivo_{cancion_idx}",
                )
                acordes_c_transp = transponer_texto_acordes(acordes_c, st_sem)

                renderizar_bloques_color(acordes_c_transp)

            else:
                for i, nombre_c in enumerate(info_servicio["canciones"], 1):
                    acordes_c = "Acordes no registrados"
                    for c_item in cancionero.values():
                        if c_item.get("titulo_real") == nombre_c:
                            acordes_c = c_item["acordes"]
                            break
                    with st.expander(f"🎵 {i}. {nombre_c}", expanded=True):
                        col_t1, col_t2 = st.columns([3, 1])
                        with col_t2:
                            sem_sutil = st.number_input(
                                "Tono",
                                min_value=-6,
                                max_value=6,
                                value=0,
                                step=1,
                                key=f"trans_sutil_{clave_fecha}_{i}",
                                help="Ajustar semitonos en vivo",
                            )

                        acordes_finales = transponer_texto_acordes(
                            acordes_c, sem_sutil
                        )
                        renderizar_bloques_color(acordes_finales)

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
                # Se asigna el número secuencial automáticamente
                titulo_final = formatear_titulo_con_numero(nuevo_titulo, len(cancionero))
                
                clave_nueva = (
                    re.sub(r"^\d+\.\s*", "", titulo_final)
                    .lower()
                    .strip()
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                )
                cancionero[clave_nueva] = {
                    "titulo_real": titulo_final,
                    "acordes": nuevos_acordes.strip(),
                }
                db["canciones"] = cancionero
                if guardar_datos_nube(db):
                    st.success(f"¡Canción guardada como '{titulo_final}'!")
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

                        titulo_elem = soup.find("h1", class_="t1") or soup.find("h1")
                        titulo_real = (
                            titulo_elem.get_text(strip=True)
                            if titulo_elem
                            else "Nueva Canción"
                        )

                        cifra_pre = soup.find("pre")
                        texto_resumido = cifra_pre.get_text() if cifra_pre else ""

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
                            st.error("No se pudo identificar la estructura.")
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
            # Se asigna el número secuencial automáticamente
            titulo_final = formatear_titulo_con_numero(titulo_f, len(cancionero))

            clave_nueva = (
                re.sub(r"^\d+\.\s*", "", titulo_final)
                .lower()
                .strip()
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            cancionero[clave_nueva] = {
                "titulo_real": titulo_final,
                "acordes": acordes_f.strip(),
            }
            db["canciones"] = cancionero
            if guardar_datos_nube(db):
                st.success(f"¡Canción guardada como '{titulo_final}'!")
                del st.session_state["temp_titulo"]
                del st.session_state["temp_acordes"]
                st.rerun()
