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
    
    <!-- Tesseract OCR -->
    <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>

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
            --radius-xl: 24px;
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

        /* --- Header Top --- */
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

        /* --- Main Content Area --- */
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 16px;
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* --- Glass Cards & Inputs --- */
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
            transition: all 0.3s ease;
        }

        .input-field:focus {
            border-color: var(--accent-neon);
            box-shadow: 0 0 12px rgba(0, 242, 254, 0.2);
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

        /* --- Buttons --- */
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
            transition: all 0.2s ease;
        }

        .btn:active {
            transform: scale(0.96);
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

        /* --- List Elements --- */
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
            transition: all 0.2s ease;
        }

        .song-item:hover, .song-item:active {
            background: rgba(0, 242, 254, 0.08);
            border-color: rgba(0, 242, 254, 0.3);
        }

        .song-info {
            display: flex;
            align-items: center;
            gap: 12px;
            overflow: hidden;
        }

        /* Badge ID Neón */
        .code-badge {
            background: rgba(0, 242, 254, 0.12);
            color: var(--accent-neon);
            border: 1px solid rgba(0, 242, 254, 0.3);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
            white-space: nowrap;
        }

        .song-details h4 {
            font-size: 1rem;
            font-weight: 600;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .song-details p {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        /* --- View Reader (Canción Abierta) --- */
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
            flex-wrap: wrap;
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
            word-break: break-word;
            color: #e2e8f0;
        }

        .chord-content .chord {
            color: var(--chord-color);
            font-weight: 700;
        }

        /* --- Barres de Controles Flotantes (Auto-Scroll) --- */
        .autoscroll-bar {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(22, 27, 34, 0.9);
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

        /* --- Bottom Navigation iOS 18 --- */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0; right: 0;
            height: var(--nav-height);
            background: rgba(15, 18, 25, 0.85);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
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
            text-decoration: none;
            font-size: 0.75rem;
            font-weight: 500;
            background: none;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 25%;
        }

        .nav-item i {
            width: 22px;
            height: 22px;
            transition: all 0.2s ease;
        }

        .nav-item.active {
            color: var(--accent-neon);
        }

        .nav-item.active i {
            transform: translateY(-2px);
        }

        /* OCR Loading Spinner */
        .ocr-loading {
            display: none;
            text-align: center;
            padding: 12px;
            color: var(--accent-neon);
            font-size: 0.9rem;
        }

        .setlist-badge {
            font-size: 0.75rem;
            background: rgba(157, 78, 221, 0.2);
            color: #d8b4fe;
            border: 1px solid rgba(157, 78, 221, 0.4);
            padding: 2px 6px;
            border-radius: 4px;
        }
    </style>
</head>
<body>

    <!-- App Header -->
    <header class="app-header">
        <div class="app-title">
            <i data-lucide="music"></i> Chords App
        </div>
        <span id="cloud-status" class="code-badge" style="background:rgba(255,255,255,0.05); color:var(--text-muted); border-color:var(--glass-border);">
            Local Mode
        </span>
    </header>

    <!-- App Container -->
    <main class="container">

        <!-- TAB 1: REPERTORIO / CANCIONES -->
        <section id="tab-songs" class="tab-content active">
            <div class="search-box">
                <i data-lucide="search"></i>
                <input type="text" id="search-input" class="input-field" placeholder="Buscar por código (#001), título o artista...">
            </div>

            <div id="songs-list">
                <!-- Las canciones se renderizan dinámicamente aquí -->
            </div>
        </section>

        <!-- TAB 2: AGREGAR / OCR -->
        <section id="tab-add" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 14px; display:flex; align-items:center; gap:8px;">
                    <i data-lucide="plus-circle" style="color:var(--accent-neon)"></i> Agregar Nueva Canción
                </h3>

                <!-- Tesseract OCR Input -->
                <div class="form-group" style="background: rgba(0,242,254,0.05); padding: 12px; border-radius: var(--radius-md); border: 1px dashed rgba(0,242,254,0.3); margin-bottom: 16px;">
                    <label style="color:var(--accent-neon); font-weight:600;"><i data-lucide="camera" style="width:14px;"></i> Escanear con OCR (Imagen a Acordes)</label>
                    <input type="file" id="ocr-file" accept="image/*" class="input-field" style="padding: 8px;">
                    <div id="ocr-spinner" class="ocr-loading">
                        ⏳ Escaneando imagen y detectando texto...
                    </div>
                </div>

                <div class="form-group">
                    <label>Título de la Canción</label>
                    <input type="text" id="song-title" class="input-field" placeholder="Ej: Tu Fidelidad" style="padding-left:14px;">
                </div>

                <div class="form-group">
                    <label>Artista / Banda</label>
                    <input type="text" id="song-artist" class="input-field" placeholder="Ej: Marcos Witt" style="padding-left:14px;">
                </div>

                <div class="form-group">
                    <label>Tono Base</label>
                    <input type="text" id="song-key" class="input-field" placeholder="Ej: C, Dm, G" style="padding-left:14px;">
                </div>

                <div class="form-group">
                    <label>Letra y Acordes</label>
                    <textarea id="song-body" class="input-field" placeholder="C             G&#10;Tu fidelidad es grande..."></textarea>
                </div>

                <button class="btn btn-primary" style="width: 100%;" onclick="saveNewSong()">
                    <i data-lucide="save"></i> Guardar Canción
                </button>
            </div>
        </section>

        <!-- TAB 3: SETLISTS / REPERTORIOS DE EVENTOS -->
        <section id="tab-setlists" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 14px; display:flex; align-items:center; gap:8px;">
                    <i data-lucide="list-music" style="color:var(--accent-purple)"></i> Crear Nuevo Setlist
                </h3>
                <div style="display:flex; gap:8px; margin-bottom: 14px;">
                    <input type="text" id="setlist-name-input" class="input-field" placeholder="Ej: Domingo Mañana" style="padding-left:14px;">
                    <button class="btn btn-purple" onclick="createSetlist()">Crear</button>
                </div>
            </div>

            <div id="setlists-container">
                <!-- Se renderizan los Setlists aquí -->
            </div>
        </section>

        <!-- TAB 4: CONFIGURACIÓN & NUBE -->
        <section id="tab-settings" class="tab-content">
            <div class="glass-card">
                <h3 style="margin-bottom: 14px; display:flex; align-items:center; gap:8px;">
                    <i data-lucide="cloud" style="color:var(--accent-neon)"></i> Sincronización JSONBin
                </h3>
                <div class="form-group">
                    <label>JSONBin Bin ID</label>
                    <input type="text" id="cfg-bin-id" class="input-field" style="padding-left:14px;" placeholder="Ej: 64aef...">
                </div>
                <div class="form-group">
                    <label>JSONBin Master Key / API Key</label>
                    <input type="password" id="cfg-api-key" class="input-field" style="padding-left:14px;" placeholder="$2a$10$...">
                </div>
                <div style="display: flex; gap: 10px; margin-top: 14px;">
                    <button class="btn btn-primary" style="flex:1;" onclick="syncWithCloud()">
                        <i data-lucide="upload-cloud"></i> Sincronizar
                    </button>
                    <button class="btn" style="flex:1;" onclick="saveCloudCredentials()">
                        Guardar Keys
                    </button>
                </div>
            </div>

            <div class="glass-card">
                <h3 style="margin-bottom: 14px;">Respaldos Locales</h3>
                <div style="display: flex; gap: 10px;">
                    <button class="btn" style="flex:1;" onclick="exportJSON()">Exportar JSON</button>
                    <button class="btn" style="flex:1;" onclick="document.getElementById('import-file').click()">Importar JSON</button>
                    <input type="file" id="import-file" style="display:none;" accept=".json" onchange="importJSON(event)">
                </div>
            </div>
        </section>

    </main>

    <!-- READER VIEW (PANTALLA COMPLETA DE LECTURA DE CANCIÓN) -->
    <div id="reader-view">
        <div class="reader-header">
            <button class="btn btn-sm" onclick="closeReader()">
                <i data-lucide="arrow-left"></i> Volver
            </button>
            <div style="text-align: center;">
                <span id="reader-code" class="code-badge">#000</span>
                <h3 id="reader-title" style="font-size: 1.1rem; margin-top: 2px;">Título</h3>
            </div>
            <button class="btn btn-sm" onclick="deleteCurrentSong()" style="color:#ff4d4d;">
                <i data-lucide="trash-2"></i>
            </button>
        </div>

        <div class="reader-controls">
            <div>
                <span style="font-size:0.8rem; color:var(--text-muted)">Transponer:</span>
                <button class="btn btn-sm" onclick="transpose(-1)">-1</button>
                <span id="current-transpose" style="font-weight:700; margin:0 4px; color:var(--accent-neon)">0</span>
                <button class="btn btn-sm" onclick="transpose(1)">+1</button>
            </div>
            <div>
                <button class="btn btn-sm btn-purple" onclick="toggleAutoScroll()">
                    <i data-lucide="play" id="scroll-icon"></i> Auto-Scroll
                </button>
            </div>
        </div>

        <div id="reader-body" class="chord-content"></div>

        <!-- Controles flotantes de Auto-Scroll -->
        <div id="autoscroll-bar" class="autoscroll-bar" style="display: none;">
            <span style="font-size: 0.8rem; font-weight: 600;">Scroll Speed:</span>
            <button class="btn btn-sm" onclick="adjustScrollSpeed(-1)">-</button>
            <span id="scroll-speed-label" style="font-family:'JetBrains Mono'; color:var(--accent-neon);">1x</span>
            <button class="btn btn-sm" onclick="adjustScrollSpeed(1)">+</button>
            <button class="btn btn-sm" onclick="toggleAutoScroll()" style="background:rgba(255,255,255,0.1); border:none;">✕</button>
        </div>
    </div>

    <!-- Bottom Navigation Bar (iOS 18 Style) -->
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
        <button class="nav-item" onclick="switchTab('settings')">
            <i data-lucide="settings"></i>
            <span>Ajustes</span>
        </button>
    </nav>

    <script>
        // Global State
        let songs = JSON.parse(localStorage.getItem('chords_songs')) || [];
        let setlists = JSON.parse(localStorage.getItem('chords_setlists')) || [];
        let currentSong = null;
        let transposeValue = 0;
        
        // Auto-Scroll State
        let autoScrollInterval = null;
        let autoScrollSpeed = 2; // Default speed

        // Initialization
        document.addEventListener('DOMContentLoaded', () => {
            lucide.createIcons();
            ensureSongCodes();
            renderSongs();
            renderSetlists();
            loadCloudCredentials();

            // Search filter listener
            document.getElementById('search-input').addEventListener('input', (e) => {
                renderSongs(e.target.value.toLowerCase());
            });

            // OCR Event listener
            document.getElementById('ocr-file').addEventListener('change', handleOCR);
        });

        // Generar códigos automáticos (#001, #002) para canciones
        function ensureSongCodes() {
            let updated = false;
            songs.forEach((song, index) => {
                const codeStr = `#${String(index + 1).padStart(3, '0')}`;
                if (song.code !== codeStr) {
                    song.code = codeStr;
                    updated = true;
                }
            });
            if (updated) saveSongsToStorage();
        }

        function saveSongsToStorage() {
            localStorage.setItem('chords_songs', JSON.stringify(songs));
        }

        function saveSetlistsToStorage() {
            localStorage.setItem('chords_setlists', JSON.stringify(setlists));
        }

        // --- Navigation / Tabs ---
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            document.getElementById(`tab-${tabId}`).classList.add('active');
            
            // Highlight nav button
            const navMap = { 'songs': 0, 'add': 1, 'setlists': 2, 'settings': 3 };
            document.querySelectorAll('.nav-item')[navMap[tabId]].classList.add('active');
        }

        // --- Render Songs List ---
        function renderSongs(filter = '') {
            const container = document.getElementById('songs-list');
            container.innerHTML = '';

            const filtered = songs.filter(s => 
                (s.code && s.code.toLowerCase().includes(filter)) ||
                s.title.toLowerCase().includes(filter) ||
                (s.artist && s.artist.toLowerCase().includes(filter))
            );

            if (filtered.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding: 40px; color: var(--text-muted);">No se encontraron canciones.</div>`;
                return;
            }

            filtered.forEach(song => {
                const item = document.createElement('div');
                item.className = 'song-item';
                item.onclick = () => openReader(song.id);
                item.innerHTML = `
                    <div class="song-info">
                        <span class="code-badge">${song.code || '#000'}</span>
                        <div class="song-details">
                            <h4>${escapeHtml(song.title)}</h4>
                            <p>${escapeHtml(song.artist || 'Artista Desconocido')} • Tono: ${song.key || 'N/A'}</p>
                        </div>
                    </div>
                    <i data-lucide="chevron-right" style="color:var(--text-muted); width:18px;"></i>
                `;
                container.appendChild(item);
            });
            lucide.createIcons();
        }

        // --- Add Song ---
        function saveNewSong() {
            const title = document.getElementById('song-title').value.trim();
            const artist = document.getElementById('song-artist').value.trim();
            const key = document.getElementById('song-key').value.trim();
            const body = document.getElementById('song-body').value.trim();

            if (!title || !body) {
                alert('Por favor agrega al menos el título y el contenido con los acordes.');
                return;
            }

            const newSong = {
                id: Date.now().toString(),
                code: `#${String(songs.length + 1).padStart(3, '0')}`,
                title,
                artist,
                key,
                body
            };

            songs.push(newSong);
            saveSongsToStorage();
            
            // Limpiar formulario y cambiar a lista
            document.getElementById('song-title').value = '';
            document.getElementById('song-artist').value = '';
            document.getElementById('song-key').value = '';
            document.getElementById('song-body').value = '';
            
            renderSongs();
            switchTab('songs');
        }

        // --- Reader View & Transposition ---
        function openReader(songId) {
            currentSong = songs.find(s => s.id === songId);
            if (!currentSong) return;

            transposeValue = 0;
            document.getElementById('current-transpose').innerText = '0';
            document.getElementById('reader-code').innerText = currentSong.code || '#000';
            document.getElementById('reader-title').innerText = currentSong.title;

            renderSongBody();
            document.getElementById('reader-view').style.display = 'block';
        }

        function closeReader() {
            stopAutoScroll();
            document.getElementById('reader-view').style.display = 'none';
        }

        function deleteCurrentSong() {
            if (!currentSong) return;
            if (confirm(`¿Seguro que deseas eliminar "${currentSong.title}"?`)) {
                songs = songs.filter(s => s.id !== currentSong.id);
                ensureSongCodes();
                saveSongsToStorage();
                renderSongs();
                closeReader();
            }
        }

        const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
        const NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];

        function transpose(semitones) {
            transposeValue += semitones;
            document.getElementById('current-transpose').innerText = (transposeValue > 0 ? '+' : '') + transposeValue;
            renderSongBody();
        }

        function transposeChord(chord, semitones) {
            return chord.replace(/[A-G][#b]?/g, match => {
                let index = NOTES.indexOf(match);
                if (index === -1) index = NOTES_FLAT.indexOf(match);
                if (index === -1) return match;
                
                let newIndex = (index + semitones) % 12;
                if (newIndex < 0) newIndex += 12;
                return NOTES[newIndex];
            });
        }

        function renderSongBody() {
            if (!currentSong) return;
            
            let text = escapeHtml(currentSong.body);
            // Detectar acordes y aplicar la transposición
            const chordRegex = /\b([A-G][#b]?(?:m|maj7|min7|dim|aug|sus2|sus4|7|9|11|13)?(?:\/[A-G][#b]?)?)\b/g;

            const transposedText = text.replace(chordRegex, (match) => {
                const transposed = transposeChord(match, transposeValue);
                return `<span class="chord">${transposed}</span>`;
            });

            document.getElementById('reader-body').innerHTML = transposedText;
        }

        // --- Auto-Scroll Feature ---
        function toggleAutoScroll() {
            if (autoScrollInterval) {
                stopAutoScroll();
            } else {
                startAutoScroll();
            }
        }

        function startAutoScroll() {
            const reader = document.getElementById('reader-view');
            document.getElementById('autoscroll-bar').style.display = 'flex';
            document.getElementById('scroll-icon').setAttribute('data-lucide', 'pause');
            lucide.createIcons();

            autoScrollInterval = setInterval(() => {
                reader.scrollTop += 1;
                // Si llega al final, detener
                if (reader.scrollTop + reader.clientHeight >= reader.scrollHeight) {
                    stopAutoScroll();
                }
            }, 50 / autoScrollSpeed);
        }

        function stopAutoScroll() {
            if (autoScrollInterval) {
                clearInterval(autoScrollInterval);
                autoScrollInterval = null;
            }
            document.getElementById('autoscroll-bar').style.display = 'none';
            document.getElementById('scroll-icon').setAttribute('data-lucide', 'play');
            lucide.createIcons();
        }

        function adjustScrollSpeed(delta) {
            autoScrollSpeed = Math.max(1, Math.min(5, autoScrollSpeed + delta));
            document.getElementById('scroll-speed-label').innerText = `${autoScrollSpeed}x`;
            if (autoScrollInterval) {
                stopAutoScroll();
                startAutoScroll();
            }
        }

        // --- Setlists (Listas de Reproducción) ---
        function createSetlist() {
            const nameInput = document.getElementById('setlist-name-input');
            const name = nameInput.value.trim();
            if (!name) return;

            const newSetlist = {
                id: Date.now().toString(),
                name: name,
                songIds: []
            };

            setlists.push(newSetlist);
            saveSetlistsToStorage();
            nameInput.value = '';
            renderSetlists();
        }

        function renderSetlists() {
            const container = document.getElementById('setlists-container');
            container.innerHTML = '';

            if (setlists.length === 0) {
                container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-muted);">No has creado ningún setlist aún.</div>`;
                return;
            }

            setlists.forEach(setlist => {
                const card = document.createElement('div');
                card.className = 'glass-card';
                card.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h4><i data-lucide="list-music" style="width:16px;"></i> ${escapeHtml(setlist.name)}</h4>
                        <button class="btn btn-sm" onclick="deleteSetlist('${setlist.id}')" style="color:#ff4d4d; border:none; background:none;">
                            <i data-lucide="trash-2" style="width:16px;"></i>
                        </button>
                    </div>
                    <div id="setlist-songs-${setlist.id}" style="margin-bottom:10px;">
                        ${renderSetlistSongs(setlist)}
                    </div>
                    <button class="btn btn-sm" onclick="showAddSongToSetlistModal('${setlist.id}')">
                        <i data-lucide="plus" style="width:14px;"></i> Añadir Canción
                    </button>
                `;
                container.appendChild(card);
            });
            lucide.createIcons();
        }

        function renderSetlistSongs(setlist) {
            if (setlist.songIds.length === 0) return `<p style="font-size:0.8rem; color:var(--text-muted);">Sin canciones añadidas.</p>`;
            
            return setlist.songIds.map(id => {
                const song = songs.find(s => s.id === id);
                if (!song) return '';
                return `
                    <div class="song-item" style="padding:8px 12px; margin-bottom:6px;" onclick="openReader('${song.id}')">
                        <span class="code-badge" style="font-size:0.75rem;">${song.code}</span>
                        <span style="font-size:0.9rem; flex:1; margin-left:8px;">${escapeHtml(song.title)}</span>
                    </div>
                `;
            }).join('');
        }

        function showAddSongToSetlistModal(setlistId) {
            const songTitle = prompt("Escribe el código (#001) o título exacto de la canción para añadirla al Setlist:");
            if (!songTitle) return;

            const song = songs.find(s => s.code.toLowerCase() === songTitle.toLowerCase() || s.title.toLowerCase().includes(songTitle.toLowerCase()));
            if (song) {
                const setlist = setlists.find(sl => sl.id === setlistId);
                if (setlist && !setlist.songIds.includes(song.id)) {
                    setlist.songIds.push(song.id);
                    saveSetlistsToStorage();
                    renderSetlists();
                }
            } else {
                alert("Canción no encontrada.");
            }
        }

        function deleteSetlist(id) {
            setlists = setlists.filter(sl => sl.id !== id);
            saveSetlistsToStorage();
            renderSetlists();
        }

        // --- Tesseract OCR Engine ---
        async function handleOCR(e) {
            const file = e.target.files[0];
            if (!file) return;

            const spinner = document.getElementById('ocr-spinner');
            spinner.style.display = 'block';

            try {
                const worker = await Tesseract.createWorker('spa');
                const ret = await worker.recognize(file);
                await worker.terminate();

                document.getElementById('song-body').value = ret.data.text;
                alert('¡Imagen procesada con éxito!');
            } catch (err) {
                console.error(err);
                alert('Error al escanear la imagen.');
            } finally {
                spinner.style.display = 'none';
            }
        }

        // --- JSONBin Cloud Sync ---
        function saveCloudCredentials() {
            const binId = document.getElementById('cfg-bin-id').value.trim();
            const apiKey = document.getElementById('cfg-api-key').value.trim();
            localStorage.setItem('chords_bin_id', binId);
            localStorage.setItem('chords_api_key', apiKey);
            alert('Credenciales guardadas.');
        }

        function loadCloudCredentials() {
            const binId = localStorage.getItem('chords_bin_id') || '';
            const apiKey = localStorage.getItem('chords_api_key') || '';
            document.getElementById('cfg-bin-id').value = binId;
            document.getElementById('cfg-api-key').value = apiKey;
            if (binId && apiKey) {
                document.getElementById('cloud-status').innerText = 'Cloud Linked';
                document.getElementById('cloud-status').style.color = 'var(--accent-neon)';
            }
        }

        async function syncWithCloud() {
            const binId = localStorage.getItem('chords_bin_id');
            const apiKey = localStorage.getItem('chords_api_key');

            if (!binId || !apiKey) {
                alert('Configura Bin ID y Master Key primero.');
                return;
            }

            try {
                const response = await fetch(`https://api.jsonbin.io/v3/b/${binId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Master-Key': apiKey
                    },
                    body: JSON.stringify({ songs, setlists })
                });

                if (response.ok) {
                    alert('¡Base de datos sincronizada con JSONBin!');
                } else {
                    alert('Error de sincronización con la nube.');
                }
            } catch (err) {
                console.error(err);
                alert('Error al conectar con JSONBin.');
            }
        }

        // --- Local Export/Import ---
        function exportJSON() {
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ songs, setlists }, null, 2));
            const dlAnchor = document.createElement('a');
            dlAnchor.setAttribute("href", dataStr);
            dlAnchor.setAttribute("download", `chords_backup_${Date.now()}.json`);
            document.body.appendChild(dlAnchor);
            dlAnchor.click();
            dlAnchor.remove();
        }

        function importJSON(e) {
            const fileReader = new FileReader();
            fileReader.onload = (event) => {
                try {
                    const parsed = JSON.parse(event.target.result);
                    if (parsed.songs) {
                        songs = parsed.songs;
                        setlists = parsed.setlists || [];
                        ensureSongCodes();
                        saveSongsToStorage();
                        saveSetlistsToStorage();
                        renderSongs();
                        renderSetlists();
                        alert('¡Datos importados con éxito!');
                    }
                } catch (err) {
                    alert('Archivo JSON no válido.');
                }
            };
            fileReader.readAsText(e.target.files[0]);
        }

        // Utility
        function escapeHtml(str) {
            return (str || '').replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
