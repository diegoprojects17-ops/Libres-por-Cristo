from datetime import datetime
import json
import re
import urllib.parse
from PIL import Image
import requests
import streamlit as st

# 1. Configuración de la página
st.set_page_config(
    page_title="Libres por Cristo", page_icon="🎹", layout="centered"
)

# Estilos CSS personalizados (Modo oscuro OLED + Chips de colores para secciones e indicador de Tono)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #090d16;
        color: #f8fafc;
    }
    div[data-testid="stCodeBlock"] {
        background-color: #020617 !important;
        border-left: 5px solid #38bdf8 !important;
    }
    .badge-tono { background-color: #0284c7; color: #ffffff; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 16px; display: inline-block; margin-bottom: 15px; border: 1px solid #38bdf8; }
    .badge-intro { background-color: #1e3a8a; color: #93c5fd; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-estrofa { background-color: #065f46; color: #6ee7b7; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-coro { background-color: #854d0e; color: #fde047; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-precoro { background-color: #9a3412; color: #fdba74; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-puente { background-color: #581c87; color: #c084fc; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-default { background-color: #334155; color: #cbd5e1; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
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


# 4. LÓGICA DE TRANSPOSICIÓN CORREGIDA Y DETECCIÓN DE TONO
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
    """Transpone únicamente los bloques de acordes sin alterar el nombre de las etiquetas."""
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

            # Transponemos SOLAMENTE la sección de acordes
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
    """Detecta el primer acorde relevante de la canción para mostrar el tono."""
    patron_acorde = (
        r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add)?[0-9]?(?:\/[A-G][#b]?)?\b"
    )
    acordes = re.findall(patron_acorde, texto_acordes)
    if acordes:
        return acordes[0]
    return "N/A"


def renderizar_bloques_color(texto_acordes):
    """Convierte el formato 'Sección // Acordes //' en bloques visuales con resaltado."""
    lineas = texto_acordes.split("\n")
    html_output = ""

    # Indicador de Tono
    tono_detectado = detectar_tono_principal(texto_acordes)
    html_output += (
        f'<div class="badge-tono">🎵 Tonalidad actual: {tono_detectado}</div>'
    )

    for linea in lineas:
        if "//" in linea:
            partes = linea.split("//")
            nombre_sec = partes[0].strip()
            acordes_sec = partes[1].strip() if len(partes) > 1 else ""

            sec_lower = nombre_sec.lower()
            clase_badge = "badge-default"
            if "intro" in sec_lower:
                clase_badge = "badge-intro"
            elif "estrofa" in sec_lower or "verso" in sec_lower:
                clase_badge = "badge-estrofa"
            elif "coro" in sec_lower or "refrão" in sec_lower:
                clase_badge = "badge-coro"
            elif "pre" in sec_lower:
                clase_badge = "badge-precoro"
            elif "puente" in sec_lower or "ponte" in sec_lower:
                clase_badge = "badge-puente"

            html_output += f"""
            <div style="margin-bottom: 12px; background: #020617; padding: 10px; border-radius: 8px; border: 1px solid #1e293b;">
                <span class="{clase_badge}">{nombre_sec}</span>
                <p style="font-family: monospace; font-size: 18px; color: #38bdf8; margin: 8px 0 0 0; font-weight: bold; letter-spacing: 1px;">
                    {acordes_sec}
                </p>
            </div>
            """
        else:
            if linea.strip():
                html_output += f"<p style='font-family: monospace; font-size: 16px;'>{linea}</p>"

    st.markdown(html_output, unsafe_allow_html=True)


# 5. PARSEADOR DE CIFRA CLUB SIN MARCAS DE TIEMPO
def parsear_acordes_cifra(soup):
    cifra_pre = soup.find("pre")
    if not cifra_pre:
        return ""

    texto_completo = cifra_pre.get_text()

    # Elimina formatos de tiempo (ej. 0:00, 00:00, (1:30), 2m30s)
    texto_sin_tiempos = re.sub(
        r"\(?\b\d{1,2}:[0-5]\d\b\)?|\b\d{1,2}m\s?[0-5]?\d?s?\b",
        "",
        texto_completo,
    )

    traducciones = {
        "intro": "Intro",
        "introdução": "Intro",
        "primeira parte": "Estrofa",
        "segunda parte": "Estrofa",
        "verso": "Estrofa",
        "pré-refrão": "Pre-coro",
        "pré refrão": "Pre-coro",
        "refrão": "Coro",
        "coro": "Coro",
        "ponte": "Puente",
        "interlúdio": "Puente",
        "solo": "Solo",
        "final": "Final",
        "outro": "Final",
    }

    patron_acorde = r"^[A-G][#b]?(m|maj|min|dim|aug|sus|add)?[0-9]?(\/[A-G][#b]?)?$"

    lineas = texto_sin_tiempos.split("\n")
    secciones_resumen = []
    sec_actual = None
    acordes_sec = []

    progresiones_registradas = {}
    contador_estrofas = 0

    for linea in lineas:
        linea_str = linea.strip()
        if not linea_str:
            continue

        linea_lower = (
            linea_str.lower().replace("[", "").replace("]", "").strip()
        )

        es_encabezado = False
        for clave, nombre_norm in traducciones.items():
            if clave in linea_lower:
                es_encabezado = True
                nuevo_nombre = nombre_norm
                break

        if es_encabezado:
            if sec_actual and acordes_sec:
                cadena = " ".join(acordes_sec)
                secciones_resumen.append(f"{sec_actual} // {cadena} //")
                acordes_sec = []
            sec_actual = nuevo_nombre
            continue

        palabras = linea_str.split()
        acordes_linea = [p for p in palabras if re.match(patron_acorde, p)]

        if acordes_linea:
            if not sec_actual:
                prog_key = "-".join(acordes_linea)
                if prog_key not in progresiones_registradas:
                    if contador_estrofas == 0:
                        sec_actual = "Intro"
                    elif contador_estrofas == 1:
                        sec_actual = "Estrofa"
                    else:
                        sec_actual = "Coro"
                    progresiones_registradas[prog_key] = sec_actual
                    contador_estrofas += 1
                else:
                    sec_actual = progresiones_registradas[prog_key]

            for ac in acordes_linea:
                if not acordes_sec or acordes_sec[-1] != ac:
                    acordes_sec.append(ac)

    if sec_actual and acordes_sec:
        cadena = " ".join(acordes_sec)
        secciones_resumen.append(f"{sec_actual} // {cadena} //")

    resultado_final = []
    for sec in secciones_resumen:
        if not resultado_final or resultado_final[-1] != sec:
            resultado_final.append(sec)

    return "\n".join(resultado_final)


# Carga Inicial de Datos
db = cargar_datos_nube()
cancionero = db.get("canciones", {})
calendario = db.get("calendario", {})

if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []

# Encabezado
st.markdown(
    """
    <div style='background-color: #0f172a; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; border: 1px solid #1e293b;'>
        <h1 style='color: #f8fafc; margin: 0; font-size: 26px;'>🎹 Libres por Cristo</h1>
        <p style='color: #38bdf8; margin: 5px 0 0 0; font-size: 14px;'>Cancionero Digital & Gestión de Servicios</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# BARRA LATERAL (BORRADOR DE REPERTORIO)
with st.sidebar:
    st.header("📋 Lista Borrador")
    canciones_disponibles = sorted(
        [datos["titulo_real"] for datos in cancionero.values()]
    )
    cancion_a_añadir = st.selectbox(
        "Añadir rápida al borrador:",
        ["-- Seleccionar --"] + canciones_disponibles,
    )

    if (
        st.button("➕ Añadir borrador")
        and cancion_a_añadir != "-- Seleccionar --"
    ):
        if cancion_a_añadir not in st.session_state.lista_servicio:
            st.session_state.lista_servicio.append(cancion_a_añadir)
            st.success(f"¡{cancion_a_añadir} agregada!")
        else:
            st.warning("Ya está en tu borrador.")

    st.write("---")
    if st.session_state.lista_servicio:
        st.write("**Canciones seleccionadas:**")
        for i, cancion in enumerate(st.session_state.lista_servicio, 1):
            st.write(f"**{i}. {cancion}**")

        if st.button("🗑️ Limpiar borrador"):
            st.session_state.lista_servicio = []
            st.rerun()

# PESTAÑAS PRINCIPALES
pestana_buscar, pestana_calendario, pestana_agregar = st.tabs([
    "🔍 Buscar Canciones",
    "📅 Calendario de Servicios",
    "➕ Agregar Canción",
])

# --- PESTAÑA 1: BUSCADOR DE CANCIONES ---
with pestana_buscar:
    busqueda = st.text_input(
        "🔍 Busca por título de canción:",
        placeholder="Ej: Cuan Grande es Él...",
    )
    busqueda_limpia = busqueda.lower().strip()

    if busqueda_limpia:
        coincidencias = [c for c in cancionero.keys() if busqueda_limpia in c]

        if not coincidencias:
            st.error("❌ No se encontró ninguna canción.")
        else:
            opciones_pantalla = {
                cancionero[c]["titulo_real"]: c for c in coincidencias
            }
            seleccion = st.selectbox(
                "Resultados encontrados:", list(opciones_pantalla.keys())
            )
            clave_sel = opciones_pantalla[seleccion]
            cancion = cancionero[clave_sel]

            st.subheader(f"🎵 {cancion['titulo_real']}")

            # Transposición interactiva rápida
            semitonos_v = st.slider(
                "Transponer tono en vivo (Semitonos):", -6, 6, 0
            )
            acordes_mostrados = transponer_texto_acordes(
                cancion["acordes"], semitonos_v
            )

            # Visualización con bloques de colores e indicador de tono
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

            st.write("---")

            # MODO EN VIVO INTERACTIVO (CARRUSEL)
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
                    if c_item["titulo_real"] == nombre_c:
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
                        if c_item["titulo_real"] == nombre_c:
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
    st.subheader("📝 Registrar nueva canción")
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
        st.write("---")
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
