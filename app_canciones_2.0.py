from datetime import datetime
import json
import re
from PIL import Image
import requests
import streamlit as st

# 1. Configuración de la página
st.set_page_config(
    page_title="Libres por Cristo", page_icon="🎹", layout="centered"
)

# Estilo visual
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
    unsafe_allow_html=True,
)

# 2. CONFIGURACIÓN DE BASE DE DATOS Y CLAVES
BIN_ID = st.secrets.get("BIN_ID", "6a5f89cada38895dfe7b600f")
MASTER_KEY = st.secrets.get(
    "MASTER_KEY", "$2a$10$vknOXY8VuZW.tNRDuxItD.5YSkYK1V8hGisTCx56w3VwGCUDLLw0i"
)
OCR_KEY = st.secrets.get("OCR_KEY", "K87431578588957")

# 3. FUNCIONES DE BASE DE DATOS EN LA NUBE
URL_JSONBIN = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"Content-Type": "application/json", "X-Master-Key": MASTER_KEY}


# Cargar datos desde la nube
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


# Guardar datos permanentes en la nube
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


# LÓGICA DE TRANSPOSICIÓN DE ACORDES
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
        palabras = linea.split()
        if palabras and sum(
            1 for p in palabras if re.match(r"^[A-G][#b]?", p)
        ) >= len(palabras) * 0.5:
            lineas_transp.append(transponer_acorde(linea, semitonos))
        else:
            lineas_transp.append(linea)
    return "\n".join(lineas_transp)


# Cargar la base de datos activa
db = cargar_datos_nube()
cancionero = db.get("canciones", {})
calendario = db.get("calendario", {})

if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []

# Encabezado principal
st.markdown(
    """
    <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
        <h1 style='color: #f8fafc; margin: 0; font-size: 26px;'>🎹 Libres por Cristo</h1>
        <p style='color: #38bdf8; margin: 5px 0 0 0; font-size: 14px;'>Agenda y lista de canciones digital</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# BARRA LATERAL (BORRADOR)
# ==========================================
with st.sidebar:
    st.header("📋 Lista Borrador")

    canciones_disponibles = [
        datos["titulo_real"] for datos in cancionero.values()
    ]
    cancion_a_añadir = st.selectbox(
        "Añadir canción al borrador:",
        ["-- Seleccionar --"] + canciones_disponibles,
    )

    if (
        st.button("➕ Añadir borrador")
        and cancion_a_añadir != "-- Seleccionar --"
    ):
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
    "➕ Agregar Canción",
])

# --- PESTAÑA 1: BUSCADOR ---
with pestana_buscar:
    busqueda = st.text_input(
        "🔍 Busca por nombre de canción o palabra clave:", ""
    )
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
            opciones_pantalla = {
                cancionero[c]["titulo_real"]: c for c in coincidencias
            }
            seleccion = st.selectbox(
                "Elige la canción:", list(opciones_pantalla.keys())
            )
            clave_seleccionada = opciones_pantalla[seleccion]

        if clave_seleccionada:
            cancion = cancionero[clave_seleccionada]
            st.subheader(f"🎵 {cancion['titulo_real']}")

            with st.expander("🛠️ Opciones de edición / eliminar"):
                nuevos_acordes_editados = st.text_area(
                    "Editar acordes:",
                    value=cancion["acordes"],
                    height=150,
                    key=f"edit_{clave_seleccionada}",
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        "💾 Guardar Cambios",
                        key=f"btn_save_{clave_seleccionada}",
                    ):
                        cancionero[clave_seleccionada]["acordes"] = (
                            nuevos_acordes_editados.strip()
                        )
                        db["canciones"] = cancionero
                        if guardar_datos_nube(db):
                            st.success("¡Canción editada!")
                            st.rerun()
                with col2:
                    if st.button(
                        "🗑️ Eliminar", key=f"btn_del_{clave_seleccionada}"
                    ):
                        del cancionero[clave_seleccionada]
                        db["canciones"] = cancionero
                        if guardar_datos_nube(db):
                            st.success("¡Eliminada!")
                            st.rerun()

            st.code(cancion["acordes"], language="text")
    else:
        st.info(
            "Escribe arriba para buscar acordes o ve al Calendario para ver el"
            " repertorio."
        )

# --- PESTAÑA 2: CALENDARIO DE SERVICIOS ---
with pestana_calendario:
    st.subheader("📅 Agenda de Servicios y Alabanzas")

    opcion_cal = st.radio(
        "¿Qué deseas hacer?",
        ["Ver Agenda de Servicios", "Programar Nuevo Servicio ➕"],
    )

    if opcion_cal == "Programar Nuevo Servicio ➕":
        st.markdown("### 📝 Programar un Servicio")
        fecha_servicio = st.date_input("Fecha del Servicio:", datetime.now())
        tipo_servicio = st.selectbox(
            "Tipo de Servicio / Reunión:",
            [
                "Servicio Dominical",
                "Reunión de Jóvenes",
                "Servicio de Oración",
                "Especial / Evento",
            ],
        )

        st.write("**Selecciona las canciones para este día:**")
        canciones_para_fecha = st.multiselect(
            "Escribe o selecciona las canciones:",
            canciones_disponibles,
            default=(
                st.session_state.lista_servicio
                if st.session_state.lista_servicio
                else []
            ),
        )

        notas_adicionales = st.text_input(
            "Indicaciones especiales (Ej: Tocar en tono Sol, ensayo a las 4"
            " PM):"
        )

        if st.button("💾 Guardar en la Agenda"):
            if canciones_para_fecha:
                fecha_str = fecha_servicio.strftime("%Y-%m-%d")

                db["calendario"][fecha_str] = {
                    "tipo": tipo_servicio,
                    "canciones": canciones_para_fecha,
                    "notas": notas_adicionales,
                }
                if guardar_datos_nube(db):
                    st.success(f"¡Servicio para el {fecha_str} guardado!")
                    st.session_state.lista_servicio = []
                    st.rerun()
            else:
                st.error("Selecciona al menos una canción.")

    elif opcion_cal == "Ver Agenda de Servicios":
        if not calendario:
            st.info(
                "Aún no hay servicios programados en la agenda. ¡Programa el"
                " primero!"
            )
        else:
            fechas_ordenadas = sorted(calendario.keys(), reverse=False)
            fechas_formateadas = {
                datetime.strptime(f, "%Y-%m-%d").strftime("%d/%m/%Y")
                + f" - {calendario[f]['tipo']}": f
                for f in fechas_ordenadas
            }

            seleccion_fecha_label = st.selectbox(
                "Elige la fecha a consultar:", list(fechas_formateadas.keys())
            )
            clave_fecha = fechas_formateadas[seleccion_fecha_label]

            info_servicio = calendario[clave_fecha]

            st.markdown(f"### 🎼 Repertorio: {info_servicio['tipo']}")
            if info_servicio["notas"]:
                st.info(f"📌 **Nota:** {info_servicio['notas']}")

            st.write("---")

            for i, nombre_c in enumerate(info_servicio["canciones"], 1):
                acordes_c = "Acordes no encontrados"
                for c_item in cancionero.values():
                    if c_item["titulo_real"] == nombre_c:
                        acordes_c = c_item["acordes"]
                        break

                with st.expander(f"🎵 {i}. {nombre_c}", expanded=True):
                    st.code(acordes_c, language="text")

            if st.button("🗑️ Eliminar este servicio de la agenda"):
                del db["calendario"][clave_fecha]
                if guardar_datos_nube(db):
                    st.success("Servicio eliminado.")
                    st.rerun()

# --- PESTAÑA 3: AGREGAR CANCIÓN ---
with pestana_agregar:
    st.subheader("📝 Registra una nueva canción")
    metodo = st.radio(
        "Elige cómo deseas agregarla:",
        [
            "Escribir manualmente",
            "Buscar en Cifra Club / Pegar Link 🎸",
            "Tomar una foto / Cargar Imagen 📸",
        ],
    )

    if metodo == "Escribir manualmente":
        nuevo_titulo = st.text_input(
            "Nombre de la canción (Ej: Cuan grande es el):"
        )
        nuevos_acordes = st.text_area(
            "Estructura y acordes:",
            placeholder="Estrofa // G C D //\nCoro // G C D //",
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
                    st.success(f"¡{nuevo_titulo} guardada!")
                    st.rerun()
            else:
                st.error("Por favor completa el título y los acordes.")

    elif metodo == "Buscar en Cifra Club / Pegar Link 🎸":
        st.markdown("### 🎸 Extraer de Cifra Club")

        sub_metodo = st.radio(
            "Selecciona forma de búsqueda:",
            ["Por Nombre de Canción", "Pegar Enlace (URL) Directo"],
        )

        if sub_metodo == "Pegar Enlace (URL) Directo":
            url_directa = st.text_input(
                "Pega el link de la canción en Cifra Club:",
                placeholder="https://www.cifraclub.com/marcos-witt/cuan-grande-es-el/",
            )
            if st.button("📥 Importar desde URL"):
                if url_directa:
                    st.session_state["url_cifra_seleccionada"] = url_directa
                    st.session_state["nombre_cifra_temp"] = "Canción Cifra Club"
                else:
                    st.error("Ingresa una URL válida.")

        else:
            busqueda_cifra = st.text_input(
                "Escribe el nombre de la canción o artista:",
                placeholder="Ej: Cuan grande es el",
            )

            if st.button("🔍 Buscar Canción"):
                if busqueda_cifra:
                    with st.spinner("Buscando en Cifra Club..."):
                        try:
                            # API directa de sugerencias de Cifra Club
                            url_api = f"https://api.cifraclub.com.br/v2/search/?q={requests.utils.quote(busqueda_cifra)}&limit=10"
                            headers = {
                                "User-Agent": (
                                    "Mozilla/5.0 (Windows NT 10.0; Win64;"
                                    " x64) AppleWebKit/537.36 (KHTML, like"
                                    " Gecko) Chrome/120.0.0.0 Safari/537.36"
                                ),
                                "Accept": "application/json, text/plain, */*",
                                "Origin": "https://www.cifraclub.com",
                                "Referer": "https://www.cifraclub.com/",
                            }
                            res = requests.get(
                                url_api, headers=headers, timeout=10
                            )

                            if res.status_code == 200:
                                datos = res.json()
                                resultados = []

                                listado = (
                                    datos.get("docs", [])
                                    if isinstance(datos, dict)
                                    else []
                                )
                                for item in listado:
                                    if item.get("type") == "cifra" or "url" in item:
                                        artist = item.get("artist", "")
                                        title = item.get(
                                            "title", item.get("value", "")
                                        )
                                        dns = item.get("dns", "")
                                        url_path = item.get("url", "")

                                        if dns and url_path:
                                            link = f"https://www.cifraclub.com/{dns}/{url_path}/"
                                            label = (
                                                f"{title} - {artist}"
                                                if artist
                                                else title
                                            )
                                            resultados.append({
                                                "label": label,
                                                "url": link,
                                            })

                                if resultados:
                                    st.session_state["resultados_cifra"] = (
                                        resultados
                                    )
                                else:
                                    st.warning(
                                        "No se encontraron coincidencias"
                                        " exactas. Intenta con palabras clave"
                                        " más sencillas o la opción de enlace"
                                        " directo."
                                    )
                            else:
                                st.error(
                                    f"Error al conectar con Cifra Club (Código"
                                    f" {res.status_code}). Usa la opción de"
                                    " enlace directo."
                                )
                        except Exception as e:
                            st.error(f"Error en la búsqueda: {e}")
                else:
                    st.error("Escribe el nombre de una canción.")

            if (
                "resultados_cifra" in st.session_state
                and st.session_state["resultados_cifra"]
            ):
                opciones = {
                    r["label"]: r["url"]
                    for r in st.session_state["resultados_cifra"]
                }
                cancion_elegida = st.selectbox(
                    "Selecciona la versión:", list(opciones.keys())
                )

                if st.button("📥 Cargar esta versión"):
                    st.session_state["url_cifra_seleccionada"] = opciones[
                        cancion_elegida
                    ]
                    st.session_state["nombre_cifra_temp"] = cancion_elegida

        # Si ya se seleccionó una URL
        if "url_cifra_seleccionada" in st.session_state:
            st.write("---")
            st.markdown("#### 🎼 Ajustar Tonalidad y Confirmar:")

            semitonos_dict = {
                "Tono Original (Sin cambio)": 0,
                "+1 Semitono": 1,
                "+2 Semitonos (1 Tono arriba)": 2,
                "+3 Semitonos": 3,
                "+4 Semitonos (2 Tonos arriba)": 4,
                "+5 Semitonos": 5,
                "-1 Semitono": -1,
                "-2 Semitonos (1 Tono abajo)": -2,
                "-3 Semitonos": -3,
            }

            opcion_trans = st.selectbox(
                "Elige la transposición:", list(semitonos_dict.keys())
            )
            semitonos = semitonos_dict[opcion_trans]

            if st.button("✨ Procesar e Importar Acordes"):
                with st.spinner("Descargando y transponiendo acordes..."):
                    try:
                        from bs4 import BeautifulSoup

                        res = requests.get(
                            st.session_state["url_cifra_seleccionada"],
                            headers={
                                "User-Agent": (
                                    "Mozilla/5.0 (Windows NT 10.0; Win64;"
                                    " x64) AppleWebKit/537.36 (KHTML, like"
                                    " Gecko) Chrome/120.0.0.0 Safari/537.36"
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
                            else st.session_state.get(
                                "nombre_cifra_temp", "Nueva Canción"
                            )
                        )

                        cifra_pre = soup.find("pre")
                        if cifra_pre:
                            texto_raw = cifra_pre.get_text()
                            texto_transp = transponer_texto_acordes(
                                texto_raw, semitonos
                            )

                            st.session_state["temp_titulo"] = titulo_real
                            st.session_state["temp_acordes"] = texto_transp
                            st.success("¡Canción lista para guardar!")

                            del st.session_state["url_cifra_seleccionada"]
                            if "resultados_cifra" in st.session_state:
                                del st.session_state["resultados_cifra"]
                            st.rerun()
                        else:
                            st.error(
                                "No se pudieron extraer los acordes de la"
                                " página."
                            )
                    except Exception as e:
                        st.error(f"Error al descargar la canción: {e}")

    elif metodo == "Tomar una foto / Cargar Imagen 📸":
        foto = st.file_uploader(
            "Sube una foto o tómala con tu cámara:", type=["jpg", "jpeg", "png"]
        )

        if foto is not None:
            imagen_original = Image.open(foto)
            st.image(imagen_original, caption="Foto cargada", width=280)

            col_engine1, col_engine2 = st.columns(2)

            with col_engine1:
                btn_digitalizar = st.button("🪄 Digitalizar (Motor Normal)")
            with col_engine2:
                btn_digitalizar_v2 = st.button(
                    "⚡ Digitalizar (Motor Avanzado Engine 2)"
                )

            if btn_digitalizar or btn_digitalizar_v2:
                engine_usado = "2" if btn_digitalizar_v2 else "1"
                with st.spinner("Procesando imagen con OCR..."):
                    try:
                        foto.seek(0)
                        files = {
                            "file": (foto.name, foto.getvalue(), foto.type)
                        }
                        payload = {
                            "apikey": OCR_KEY,
                            "language": "spa",
                            "isOverlayRequired": "False",
                            "detectOrientation": "True",
                            "scale": "True",
                            "OCREngine": engine_usado,
                        }

                        respuesta = requests.post(
                            "https://api.ocr.space/parse/image",
                            files=files,
                            data=payload,
                            timeout=20,
                        )
                        resultado = respuesta.json()

                        if resultado.get("OCRExitCode") == 1 and resultado.get(
                            "ParsedResults"
                        ):
                            texto_extraido = resultado["ParsedResults"][0].get(
                                "ParsedText", ""
                            )

                            if texto_extraido.strip():
                                lineas = [
                                    l.strip()
                                    for l in texto_extraido.split("\n")
                                    if l.strip()
                                ]
                                if lineas:
                                    st.session_state["temp_titulo"] = lineas[0]
                                    st.session_state["temp_acordes"] = "\n".join(
                                        lineas[1:]
                                    )
                                else:
                                    st.session_state["temp_titulo"] = (
                                        "Nueva Canción"
                                    )
                                    st.session_state["temp_acordes"] = (
                                        texto_extraido
                                    )
                                st.rerun()
                            else:
                                st.error(
                                    "No se detectó texto legible. Intenta con"
                                    " el botón 'Motor Avanzado Engine 2'."
                                )
                        else:
                            mensaje_err = resultado.get(
                                "ErrorMessage", ["Error desconocido"]
                            )[0]
                            st.error(f"Error al leer la imagen: {mensaje_err}")
                    except Exception as e:
                        st.error(f"Error de conexión con el servicio OCR: {e}")

    # Bloque de Confirmación y Guardado
    if "temp_titulo" in st.session_state:
        st.write("---")
        st.subheader("🔍 Verifica y Guarda la Canción:")

        titulo_final = st.text_input(
            "Confirmar Título:", st.session_state["temp_titulo"]
        )
        acordes_finales = st.text_area(
            "Confirmar Acordes:", st.session_state["temp_acordes"], height=250
        )

        if st.button("💾 Guardar Canción en el Cancionero"):
            clave_nueva = (
                titulo_final.lower()
                .strip()
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )

            cancionero[clave_nueva] = {
                "titulo_real": titulo_final.strip(),
                "acordes": acordes_finales.strip(),
            }
            db["canciones"] = cancionero
            if guardar_datos_nube(db):
                st.success(f"¡{titulo_final} guardada exitosamente!")
                del st.session_state["temp_titulo"]
                del st.session_state["temp_acordes"]
                st.rerun()
