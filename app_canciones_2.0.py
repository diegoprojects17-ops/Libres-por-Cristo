from datetime import datetime
import json
import re
import urllib.parse

from PIL import Image
import requests
import streamlit as st
from supabase import Client, create_client

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Libres por Cristo", page_icon="🎹", layout="centered"
)

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    .stApp { background-color: #090d16; color: #f8fafc; }
    div[data-testid="stCodeBlock"] { background-color: #020617 !important; border-left: 5px solid #38bdf8 !important; }
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

# 2. CONEXIÓN A SUPABASE Y SECRETO OCR
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "TU_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "TU_SUPABASE_ANON_KEY")
OCR_KEY = st.secrets.get("OCR_KEY", "K87431578588957")


@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

# 3. GESTIÓN DE SESIÓN Y OAUTH GOOGLE
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "lista_servicio" not in st.session_state:
    st.session_state.lista_servicio = []


def login_con_google():
    res = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": "http://localhost:8501/"  # Cambia esto por la URL de producción
        },
    })
    if res.url:
        st.markdown(
            f'<a href="{res.url}" target="_self">👉 Haz clic aquí para Iniciar'
            " Sesión con Google</a>",
            unsafe_allow_html=True,
        )


session = supabase.auth.get_session()
if session and not st.session_state.usuario:
    user_data = session.user
    user_metadata = user_data.user_metadata

    perfil = {
        "id": user_data.id,
        "nombre": user_metadata.get("full_name", "Usuario"),
        "email": user_data.email,
        "foto_url": user_metadata.get("avatar_url", ""),
    }
    supabase.table("perfiles").upsert(perfil).execute()
    st.session_state.usuario = perfil

if not st.session_state.usuario:
    st.markdown(
        """
        <div style='background-color: #0f172a; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 20px; border: 1px solid #1e293b;'>
            <h1 style='color: #f8fafc; margin: 0;'>🎹 Libres por Cristo</h1>
            <p style='color: #38bdf8; margin-top: 5px;'>Plataforma para Equipos de Alabanza</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(
        "Inicia sesión para gestionar tus repertorios, transponer acordes y"
        " sincronizar servicios con tu iglesia."
    )
    if st.button("🔑 Iniciar Sesión con Google"):
        login_con_google()
    st.stop()

# 4. FUNCIONES TÉCNICAS (TRANSPOSICIÓN Y PROCESAMIENTO)
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

    return re.sub(r"([A-G][#b]?)", transponer_nota, acorde)


def transponer_texto_acordes(texto, semitonos):
    if semitonos == 0 or not texto:
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
            ) >= (len(palabras) * 0.4):
                lineas_transp.append(transponer_acorde(linea, semitonos))
            else:
                lineas_transp.append(linea)
    return "\n".join(lineas_transp)


def detectar_tono_principal(texto_acordes):
    patron_acorde = (
        r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add)?[0-9]?(?:\/[A-G][#b]?)?\b"
    )
    acordes = re.findall(patron_acorde, texto_acordes)
    return acordes[0] if acordes else "N/A"


def renderizar_bloques_color(texto_acordes):
    tono_detectado = detectar_tono_principal(texto_acordes)
    st.markdown(
        f'<div class="badge-tono">🎵 Tonalidad actual: {tono_detectado}</div>',
        unsafe_allow_html=True,
    )

    for linea in texto_acordes.split("\n"):
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
            elif "coro" in sec_lower or "refrão" in sec_lower:
                clase_badge = "badge-coro"
            elif "pre" in sec_lower:
                clase_badge = "badge-precoro"
            elif "puente" in sec_lower or "ponte" in sec_lower:
                clase_badge = "badge-puente"

            html_tarjeta = (
                f'<div style="margin-bottom: 12px; background: #020617; padding:'
                f' 10px; border-radius: 8px; border: 1px solid #1e293b;"><span'
                f' class="{clase_badge}">{nombre_sec}</span><p'
                ' style="font-family: monospace; font-size: 18px; color:'
                ' #38bdf8; margin: 8px 0 0 0; font-weight: bold; letter-spacing:'
                f' 1px;">{acordes_sec}</p></div>'
            )
            st.markdown(html_tarjeta, unsafe_allow_html=True)
        elif linea.strip():
            st.markdown(
                f"<p style='font-family: monospace; font-size:"
                f" 16px;'>{linea}</p>",
                unsafe_allow_html=True,
            )


def parsear_acordes_cifra(soup):
    cifra_pre = soup.find("pre")
    if not cifra_pre:
        return ""
    texto = re.sub(
        r"\(?\b\d{1,2}:[0-5]\d\b\)?|\b\d{1,2}m\s?[0-5]?\d?s?\b",
        "",
        cifra_pre.get_text(),
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

    secciones, sec_actual, acordes_sec = [], None, []
    progresiones, contador = {}, 0

    for linea in texto.split("\n"):
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
                secciones.append(f"{sec_actual} // {' '.join(acordes_sec)} //")
                acordes_sec = []
            sec_actual = nuevo_nombre
            continue

        acordes_linea = [
            p for p in linea_str.split() if re.match(patron_acorde, p)
        ]
        if acordes_linea:
            if not sec_actual:
                prog_key = "-".join(acordes_linea)
                if prog_key not in progresiones:
                    sec_actual = (
                        "Intro"
                        if contador == 0
                        else ("Estrofa" if contador == 1 else "Coro")
                    )
                    progresiones[prog_key] = sec_actual
                    contador += 1
                else:
                    sec_actual = progresiones[prog_key]
            for ac in acordes_linea:
                if not acordes_sec or acordes_sec[-1] != ac:
                    acordes_sec.append(ac)

    if sec_actual and acordes_sec:
        secciones.append(f"{sec_actual} // {' '.join(acordes_sec)} //")

    resultado = []
    for s in secciones:
        if not resultado or resultado[-1] != s:
            resultado.append(s)
    return "\n".join(resultado)


# 5. BARRA LATERAL: PERFIL Y GRUPOS DE ALABANZA
usuario = st.session_state.usuario

with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        if usuario.get("foto_url"):
            st.image(usuario["foto_url"], width=45)
        else:
            st.write("👤")
    with col2:
        st.write(f"**{usuario['nombre']}**")
        st.caption(usuario["email"])

    if st.button("🚪 Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.usuario = None
        st.rerun()

    st.write("---")
    st.header("👥 Mi Grupo de Alabanza")

    res_grupos = (
        supabase.table("miembros_grupo")
        .select("grupo_id, grupos(id, nombre)")
        .eq("usuario_id", usuario["id"])
        .execute()
    )
    mis_grupos = [g["grupos"] for g in res_grupos.data] if res_grupos.data else []

    if mis_grupos:
        opciones_grupos = {g["nombre"]: g["id"] for g in mis_grupos}
        grupo_sel = st.selectbox(
            "Grupo activo:", list(opciones_grupos.keys())
        )
        st.session_state.grupo_id_activo = opciones_grupos[grupo_sel]
    else:
        st.warning("No estás vinculado a ningún grupo.")
        st.session_state.grupo_id_activo = None

    with st.expander("➕ Unirse o Crear Grupo"):
        accion = st.radio("Acción:", ["Unirse con Código", "Crear Grupo"])
        if accion == "Unirse con Código":
            cod = st.text_input("Código de Invitación:")
            if st.button("Unirme"):
                g = (
                    supabase.table("grupos")
                    .select("id")
                    .eq("codigo_invitacion", cod.strip())
                    .execute()
                )
                if g.data:
                    supabase.table("miembros_grupo").insert({
                        "grupo_id": g.data[0]["id"],
                        "usuario_id": usuario["id"],
                        "rol": "músico",
                    }).execute()
                    st.success("¡Te has unido!")
                    st.rerun()
                else:
                    st.error("Código no válido.")
        else:
            nom_g = st.text_input("Nombre de la Iglesia/Grupo:")
            cod_g = st.text_input("Código (Ej: WORSHIP2026):")
            if st.button("Crear"):
                if nom_g and cod_g:
                    new_g = (
                        supabase.table("grupos")
                        .insert({
                            "nombre": nom_g,
                            "codigo_invitacion": cod_g,
                            "creado_por": usuario["id"],
                        })
                        .execute()
                    )
                    if new_g.data:
                        supabase.table("miembros_grupo").insert({
                            "grupo_id": new_g.data[0]["id"],
                            "usuario_id": usuario["id"],
                            "rol": "director",
                        }).execute()
                        st.success("¡Grupo creado!")
                        st.rerun()

    # BORRADOR DE REPERTORIO VINCULADO AL GRUPO
    if st.session_state.grupo_id_activo:
        st.write("---")
        st.header("📋 Lista Borrador")
        canciones_db = (
            supabase.table("canciones")
            .select("titulo")
            .eq("grupo_id", st.session_state.grupo_id_activo)
            .execute()
        )
        titulos_disponibles = sorted(
            [c["titulo"] for c in canciones_db.data]
        ) if canciones_db.data else []

        c_add = st.selectbox(
            "Añadir rápida al borrador:", ["-- Seleccionar --"] + titulos_disponibles
        )
        if st.button("➕ Añadir borrador") and c_add != "-- Seleccionar --":
            if c_add not in st.session_state.lista_servicio:
                st.session_state.lista_servicio.append(c_add)
                st.success(f"¡{c_add} añadida!")
            else:
                st.warning("Ya está en el borrador.")

        if st.session_state.lista_servicio:
            for idx, item in enumerate(st.session_state.lista_servicio, 1):
                st.write(f"**{idx}. {item}**")
            if st.button("🗑️ Limpiar borrador"):
                st.session_state.lista_servicio = []
                st.rerun()

# 6. PESTAÑAS PRINCIPALES DEL GRUPO ACTIVO
if not st.session_state.grupo_id_activo:
    st.info(
        "👈 Únete o crea un grupo de alabanza en la barra lateral para ver los"
        " repertorios."
    )
else:
    pestana_buscar, pestana_calendario, pestana_agregar = st.tabs([
        "🔍 Cancionero",
        "📅 Agenda de Servicios",
        "➕ Agregar Canción",
    ])

    # --- PESTAÑA 1: CANCIONERO Y BUSCADOR ---
    with pestana_buscar:
        busqueda = st.text_input(
            "🔍 Buscar canción en este grupo:", placeholder="Ej: Cuan Grande es Él"
        )
        query = (
            supabase.table("canciones")
            .select("*")
            .eq("grupo_id", st.session_state.grupo_id_activo)
        )
        if busqueda:
            query = query.ilike("titulo", f"%{busqueda.strip()}%")
        res_canciones = query.execute()

        if not res_canciones.data:
            st.info("No se encontraron canciones grabadas.")
        else:
            dict_canciones = {c["titulo"]: c for c in res_canciones.data}
            cancion_sel = st.selectbox(
                "Selecciona una canción:", list(dict_canciones.keys())
            )
            datos_c = dict_canciones[cancion_sel]

            st.subheader(f"🎵 {datos_c['titulo']}")
            semitonos_v = st.slider(
                "Transponer tono en vivo (Semitonos):", -6, 6, 0
            )
            acordes_transp = transponer_texto_acordes(
                datos_c["acordes"], semitonos_v
            )

            renderizar_bloques_color(acordes_transp)

            with st.expander("🛠️ Editar datos o acordes"):
                edit_titulo = st.text_input("Título:", value=datos_c["titulo"])
                edit_acordes = st.text_area(
                    "Acordes:", value=datos_c["acordes"], height=150
                )

                col_s, col_d = st.columns(2)
                with col_s:
                    if st.button("💾 Guardar Cambios"):
                        supabase.table("canciones").update({
                            "titulo": edit_titulo.strip(),
                            "acordes": edit_acordes.strip(),
                        }).eq("id", datos_c["id"]).execute()
                        st.success("¡Canción actualizada!")
                        st.rerun()
                with col_d:
                    if st.button("🗑️ Eliminar Canción"):
                        supabase.table("canciones").delete().eq(
                            "id", datos_c["id"]
                        ).execute()
                        st.success("Canción eliminada.")
                        st.rerun()

    # --- PESTAÑA 2: AGENDA DE SERVICIOS Y MODO EN VIVO ---
    with pestana_calendario:
        opcion_cal = st.radio(
            "Modalidad:",
            ["Ver Agenda de Servicios", "Programar Nuevo Servicio ➕"],
            horizontal=True,
        )

        if opcion_cal == "Programar Nuevo Servicio ➕":
            st.markdown("### 📝 Programar Servicio")
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

            canciones_db = (
                supabase.table("canciones")
                .select("titulo")
                .eq("grupo_id", st.session_state.grupo_id_activo)
                .execute()
            )
            todas_canciones = [c["titulo"] for c in canciones_db.data] if canciones_db.data else []

            canciones_para_fecha = st.multiselect(
                "Repertorio:",
                todas_canciones,
                default=st.session_state.lista_servicio,
            )
            notas = st.text_input("Observaciones (Ej: Tocar en Sol, Ensayo 4 PM):")

            if st.button("💾 Guardar en Agenda"):
                if canciones_para_fecha:
                    supabase.table("servicios").insert({
                        "grupo_id": st.session_state.grupo_id_activo,
                        "fecha": fecha_servicio.strftime("%Y-%m-%d"),
                        "tipo": tipo_servicio,
                        "canciones": canciones_para_fecha,
                        "notas": notas,
                        "creado_por": usuario["id"],
                    }).execute()
                    st.success("¡Servicio agendado!")
                    st.session_state.lista_servicio = []
                    st.rerun()

        elif opcion_cal == "Ver Agenda de Servicios":
            res_servicios = (
                supabase.table("servicios")
                .select("*")
                .eq("grupo_id", st.session_state.grupo_id_activo)
                .order("fecha", desc=False)
                .execute()
            )

            if not res_servicios.data:
                st.info("No hay servicios programados en este grupo.")
            else:
                dict_servicios = {
                    f"{s['fecha']} - {s['tipo']}": s for s in res_servicios.data
                }
                sel_servicio = st.selectbox(
                    "Selecciona una fecha:", list(dict_servicios.keys())
                )
                info_s = dict_servicios[sel_servicio]

                st.markdown(f"### 🎼 Repertorio: {info_s['tipo']}")
                if info_s.get("notas"):
                    st.info(f"📌 **Observación:** {info_s['notas']}")

                texto_wa = (
                    f"*REPERTORIO {info_s['tipo'].upper()}*\n📅"
                    f" *Fecha:* {info_s['fecha']}\n\n"
                )
                for idx, c_nom in enumerate(info_s["canciones"], 1):
                    texto_wa += f"{idx}. {c_nom}\n"
                if info_s.get("notas"):
                    texto_wa += f"\n📌 *Notas:* {info_s['notas']}"

                url_wa = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_wa)}"
                st.markdown(
                    f"[📲 Compartir Repertorio en WhatsApp]({url_wa})",
                    unsafe_allow_html=True,
                )

                st.write("---")

                if st.checkbox(
                    "🚀 MODO EN VIVO (Lectura Gigante para Servicio)"
                ):
                    cancion_idx = st.slider(
                        "Cambiar de canción:", 1, len(info_s["canciones"]), 1
                    )
                    nombre_c = info_s["canciones"][cancion_idx - 1]

                    res_c = (
                        supabase.table("canciones")
                        .select("acordes")
                        .eq("grupo_id", st.session_state.grupo_id_activo)
                        .eq("titulo", nombre_c)
                        .execute()
                    )
                    acordes_c = (
                        res_c.data[0]["acordes"]
                        if res_c.data
                        else "Sin acordes registrados."
                    )

                    st.markdown(
                        f"<h2 style='text-align: center; color:"
                        f" #38bdf8;'>{cancion_idx}. {nombre_c}</h2>",
                        unsafe_allow_html=True,
                    )
                    semitonos_vivo = st.slider(
                        f"Ajustar Tono (Semitonos):",
                        -6,
                        6,
                        0,
                        key=f"slider_v_{cancion_idx}",
                    )
                    renderizar_bloques_color(
                        transponer_texto_acordes(acordes_c, semitonos_vivo)
                    )

                else:
                    for i, nombre_c in enumerate(info_s["canciones"], 1):
                        res_c = (
                            supabase.table("canciones")
                            .select("acordes")
                            .eq("grupo_id", st.session_state.grupo_id_activo)
                            .eq("titulo", nombre_c)
                            .execute()
                        )
                        acordes_c = (
                            res_c.data[0]["acordes"]
                            if res_c.data
                            else "Sin acordes"
                        )
                        with st.expander(f"🎵 {i}. {nombre_c}", expanded=True):
                            renderizar_bloques_color(acordes_c)

                if st.button("🗑️ Eliminar este servicio"):
                    supabase.table("servicios").delete().eq(
                        "id", info_s["id"]
                    ).execute()
                    st.success("Servicio eliminado.")
                    st.rerun()

    # --- PESTAÑA 3: AGREGAR CANCIÓN AL GRUPO ---
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
                    supabase.table("canciones").insert({
                        "grupo_id": st.session_state.grupo_id_activo,
                        "titulo": nuevo_titulo.strip(),
                        "acordes": nuevos_acordes.strip(),
                        "creado_por": usuario["id"],
                    }).execute()
                    st.success("¡Canción guardada!")
                    st.rerun()

        elif metodo == "Pegar Link Directo de Cifra Club 🎸":
            url_directa = st.text_input(
                "Link de Cifra Club:",
                placeholder=(
                    "https://www.cifraclub.com/marcos-witt/cuan-grande-es-el/"
                ),
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

                            titulo_elem = soup.find(
                                "h1", class_="t1"
                            ) or soup.find("h1")
                            titulo_real = (
                                titulo_elem.get_text(strip=True)
                                if titulo_elem
                                else "Nueva Canción"
                            )

                            texto_resumido = parsear_acordes_cifra(soup)

                            if texto_resumido:
                                st.session_state["temp_titulo"] = titulo_real
                                st.session_state["temp_acordes"] = (
                                    transponer_texto_acordes(
                                        texto_resumido, semitonos
                                    )
                                )
                                st.success("¡Estructura extraída exitosamente!")
                                del st.session_state["url_cifra_seleccionada"]
                                st.rerun()
                            else:
                                st.error(
                                    "No se pudo identificar la estructura."
                                )
                        except Exception as e:
                            st.error(f"Error al procesar la URL: {e}")

        elif metodo == "Tomar una foto / Cargar Imagen 📸":
            foto = st.file_uploader(
                "Cargar imagen de partitura/cifrado:",
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
                                    l.strip()
                                    for l in texto.split("\n")
                                    if l.strip()
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

        # Confirmación Final
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
                supabase.table("canciones").insert({
                    "grupo_id": st.session_state.grupo_id_activo,
                    "titulo": titulo_f.strip(),
                    "acordes": acordes_f.strip(),
                    "creado_por": usuario["id"],
                }).execute()
                st.success("¡Canción guardada con éxito!")
                del st.session_state["temp_titulo"]
                del st.session_state["temp_acordes"]
                st.rerun()
