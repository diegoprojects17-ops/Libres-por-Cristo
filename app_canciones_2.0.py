import streamlit as st

st.set_page_config(page_title="Chords App", layout="wide", initial_sidebar_state="collapsed")

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chords App - iOS 18 Glass</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>

    <style>
        :root {
            --bg-base: #0a0c10;
            --glass-bg: rgba(22, 27, 34, 0.65);
            --glass-border: rgba(255, 255, 255, 0.12);
            --glass-blur: blur(20px) saturate(190%);
            --accent-neon: #00f2fe;
            --accent-purple: #9d4edd;
            --accent-gradient: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --chord-color: #00f2fe;
            --radius-lg: 16px;
            --radius-md: 12px;
            --shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            --nav-height: 70px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: calc(var(--nav-height) + 20px);
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(157, 78, 221, 0.08) 0%, transparent 40%);
            background-attachment: fixed;
        }

        .app-header {
            position: sticky;
            top: 0;
            z-index: 90;
            background: rgba(10, 12, 16, 0.75);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border-bottom: 1px solid var(--glass-border);
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .app-title {
            font-size: 1.3rem;
            font-weight: 700;
            background: linear-gradient(90deg, #fff, var(--accent-neon));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 16px;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-lg);
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: var(--shadow-glass);
        }

        .search-box {
            position: relative;
            margin-bottom: 16px;
        }

        .search-box i {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            width: 18px;
        }

        .input-field {
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--glass-border);
            border-radius: var(--radius-md);
            padding: 12px 14px 12px 42px;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
        }

        .input-field:focus {
            border-color: var(--accent-neon);
        }

        textarea.input-field {
            padding: 12px 14px;
            min-height: 120px;
            resize: vertical;
            font-family: 'JetBrains Mono', monospace;
        }

        .form-group {
            margin-bottom: 14px;
        }

        .form-group label {
            display: block;
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 6px;
        }

        .btn {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            color: var(--text-main);
            padding: 10px 16px;
            border-radius: var(--radius-md);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-primary {
            background: var(--accent-gradient);
            color: #000;
            border: none;
            font-weight: 700;
        }

        .btn-purple {
            background: linear-gradient(135deg, #9d4edd 0%, #7b2cbf 100%);
            color: #fff;
            border: none;
        }

        .btn-sm {
            padding: 6px 12px;
            font-size: 0.8rem;
            border-radius: 8px;
        }

        .song-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px;
            margin-bottom: 10px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: var(--radius-md);
            cursor: pointer;
        }

        .code-badge {
            background: rgba(0, 242, 254, 0.12);
            color: var(--accent-neon);
            border: 1px solid rgba(0, 242, 254, 0.3);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
        }

        #reader-view {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--bg-base);
            z-index: 200;
            overflow-y: auto;
            padding: 20px;
            padding-bottom: 100px;
        }

        .reader-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            position: sticky;
            top: 0;
            background: rgba(10, 12, 16, 0.85);
            backdrop-filter: var(--glass-blur);
            padding: 10px 0;
            z-index: 10;
        }

        .reader-controls {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            background: var(--glass-bg);
            padding: 12px;
            border-radius: var(--radius-lg);
            border: 1px solid var(--glass-border);
            align-items: center;
            justify-content: space-between;
        }

        .chord-content {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.05rem;
            line-height: 1.6;
            white-space: pre-wrap;
            color: #e2e8f0;
        }

        .chord-content .chord {
            color: var(--chord-color);
            font-weight: 700;
        }

        .autoscroll-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(22, 27, 34, 0.95);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--glass-border);
            padding: 10px 20px;
            border-radius: 40px;
            display: flex;
            align-items: center;
            gap: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            z-index: 210;
        }

        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0; right: 0;
            height: var(--nav-height);
            background: rgba(15, 18, 25, 0.85);
            backdrop-filter: var(--glass-blur);
            border-top: 1px solid var(--glass-border);
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 100;
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            color: var(--text-muted);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 0.75rem;
            width: 33%;
        }

        .nav-item.active {
            color: var(--accent-neon);
        }
    </style>
</head>
<body>

    <header class="app-header">
        <div class="app-title">
            <i data-lucide="music"></i> Chords App
        </div>
    </header>

    <main class="container">
        <!-- Pestaña Canciones -->
        <section id="tab-songs" class="tab-content active">
            <div class="search-box">
                <i data-lucide="search"></i>
                <input type="text" id="search-input" class="input-field" placeholder="Buscar canción...">
            </div>

            <div id="songs-list"></div>
        </section>

        <!-- Pestaña Agregar -->
        <section id="tab-add" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 14px;"><i data-lucide="plus-circle"></i> Agregar Canción</h3>
                <div class="form-group">
                    <label>Título</label>
                    <input type="text" id="song-title" class="input-field" style="padding-left:14px;">
                </div>
                <div class="form-group">
                    <label>Artista</label>
                    <input type="text" id="song-artist" class="input-field" style="padding-left:14px;">
                </div>
                <div class="form-group">
                    <label>Letra y Acordes</label>
                    <textarea id="song-body" class="input-field"></textarea>
                </div>
                <button class="btn btn-primary" style="width: 100%;" onclick="saveNewSong()">Guardar Canción</button>
            </div>
        </section>

        <!-- Pestaña Setlists (Paso 3) -->
        <section id="tab-setlists" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 14px;"><i data-lucide="list-music"></i> Crear Nuevo Setlist</h3>
                <div style="display:flex; gap:8px;">
                    <input type="text" id="setlist-name-input" class="input-field" placeholder="Nombre del setlist..." style="padding-left:14px;">
                    <button class="btn btn-purple" onclick="createSetlist()">Crear</button>
                </div>
            </div>
            <div id="setlists-container"></div>
        </section>
    </main>

    <!-- Vista de Lectura con Auto-Scroll (Paso 3) -->
    <div id="reader-view">
        <div class="reader-header">
            <button class="btn btn-sm" onclick="closeReader()"><i data-lucide="arrow-left"></i> Volver</button>
            <h3 id="reader-title">Título</h3>
            <div></div>
        </div>

        <div class="reader-controls">
            <button class="btn btn-sm btn-purple" onclick="toggleAutoScroll()">
                <i data-lucide="play" id="scroll-icon"></i> Auto-Scroll
            </button>
        </div>

        <div id="reader-body" class="chord-content"></div>

        <!-- Barra de Control de Auto-Scroll -->
        <div id="autoscroll-bar" class="autoscroll-bar" style="display: none;">
            <span style="font-size: 0.8rem;">Velocidad:</span>
            <button class="btn btn-sm" onclick="adjustScrollSpeed(-1)">-</button>
            <span id="scroll-speed-label" style="color:var(--accent-neon);">1x</span>
            <button class="btn btn-sm" onclick="adjustScrollSpeed(1)">+</button>
            <button class="btn btn-sm" onclick="toggleAutoScroll()">✕</button>
        </div>
    </div>

    <!-- Navegación Inferior -->
    <nav class="bottom-nav">
        <button class="nav-item active" onclick="switchTab('songs')">
            <i data-lucide="music"></i>
            <span>Canciones</span>
        </button>
        <button class="nav-item" onclick="switchTab('add')">
            <i data-lucide="plus-circle"></i>
            <span>Agregar</span>
        </button>
        <button class="nav-item" onclick="switchTab('setlists')">
            <i data-lucide="list-music"></i>
            <span>Setlists</span>
        </button>
    </nav>

    <script>
        let songs = JSON.parse(localStorage.getItem('chords_songs')) || [];
        let setlists = JSON.parse(localStorage.getItem('chords_setlists')) || [];
        let currentSong = null;
        let autoScrollInterval = null;
        let autoScrollSpeed = 1;

        document.addEventListener('DOMContentLoaded', () => {
            lucide.createIcons();
            renderSongs();
            renderSetlists();
        });

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            document.getElementById(`tab-${tabId}`).classList.add('active');
            const navMap = { 'songs': 0, 'add': 1, 'setlists': 2 };
            document.querySelectorAll('.nav-item')[navMap[tabId]].classList.add('active');
        }

        function renderSongs() {
            const container = document.getElementById('songs-list');
            container.innerHTML = '';
            songs.forEach(song => {
                const item = document.createElement('div');
                item.className = 'song-item';
                item.onclick = () => openReader(song.id);
                item.innerHTML = `<div><h4>${song.title}</h4><p>${song.artist}</p></div>`;
                container.appendChild(item);
            });
        }

        function saveNewSong() {
            const title = document.getElementById('song-title').value.trim();
            const artist = document.getElementById('song-artist').value.trim();
            const body = document.getElementById('song-body').value.trim();
            if (!title || !body) return;

            songs.push({ id: Date.now().toString(), title, artist, body });
            localStorage.setItem('chords_songs', JSON.stringify(songs));
            renderSongs();
            switchTab('songs');
        }

        function openReader(songId) {
            currentSong = songs.find(s => s.id === songId);
            if (!currentSong) return;
            document.getElementById('reader-title').innerText = currentSong.title;
            document.getElementById('reader-body').innerText = currentSong.body;
            document.getElementById('reader-view').style.display = 'block';
        }

        function closeReader() {
            stopAutoScroll();
            document.getElementById('reader-view').style.display = 'none';
        }

        /* --- AUTO-SCROLL (Paso 3) --- */
        function toggleAutoScroll() {
            if (autoScrollInterval) stopAutoScroll();
            else startAutoScroll();
        }

        function startAutoScroll() {
            const reader = document.getElementById('reader-view');
            document.getElementById('autoscroll-bar').style.display = 'flex';
            autoScrollInterval = setInterval(() => {
                reader.scrollTop += 1;
                if (reader.scrollTop + reader.clientHeight >= reader.scrollHeight) stopAutoScroll();
            }, 50 / autoScrollSpeed);
        }

        function stopAutoScroll() {
            if (autoScrollInterval) {
                clearInterval(autoScrollInterval);
                autoScrollInterval = null;
            }
            document.getElementById('autoscroll-bar').style.display = 'none';
        }

        function adjustScrollSpeed(delta) {
            autoScrollSpeed = Math.max(1, Math.min(5, autoScrollSpeed + delta));
            document.getElementById('scroll-speed-label').innerText = `${autoScrollSpeed}x`;
            if (autoScrollInterval) {
                stopAutoScroll();
                startAutoScroll();
            }
        }

        /* --- CREADOR DE SETLISTS (Paso 3) --- */
        function createSetlist() {
            const input = document.getElementById('setlist-name-input');
            const name = input.value.trim();
            if (!name) return;

            setlists.push({ id: Date.now().toString(), name, songIds: [] });
            localStorage.setItem('chords_setlists', JSON.stringify(setlists));
            input.value = '';
            renderSetlists();
        }

        function renderSetlists() {
            const container = document.getElementById('setlists-container');
            container.innerHTML = '';
            setlists.forEach(setlist => {
                const card = document.createElement('div');
                card.className = 'glass-card';
                card.innerHTML = `<h4>${setlist.name}</h4><p style="font-size:0.8rem; color:var(--text-muted);">${setlist.songIds.length} canciones</p>`;
                container.appendChild(card);
            });
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=900, scrolling=True)
