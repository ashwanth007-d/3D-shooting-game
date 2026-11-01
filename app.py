import streamlit as st
import os
import math
from collections import deque
import streamlit.components.v1 as components

st.set_page_config(
    page_title="DOOM 3D FPS - Raycasting Engine",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom retro DOOM cyber aesthetic
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Press+Start+2P&family=Share+Tech+Mono&display=swap');

    .main {
        background: radial-gradient(circle at 50% 20%, #1a0808 0%, #080303 100%);
        color: #f0f0f0;
        font-family: 'Share Tech Mono', monospace;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    .doom-title {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        font-size: 2.8rem;
        background: linear-gradient(180deg, #ffde59 0%, #ff5722 50%, #b71c1c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(255, 87, 34, 0.4);
        margin-bottom: 0px;
    }
    
    .doom-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
        background: rgba(255, 87, 34, 0.15);
        border: 1px solid #ff5722;
        color: #ffab91;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #b71c1c;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1a0d0d;
        border-radius: 6px 6px 0 0;
        color: #cfd8dc;
        padding: 10px 20px;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        border: 1px solid #371a1a;
        border-bottom: none;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #b71c1c 0%, #5d0909 100%) !important;
        color: #ffffff !important;
        border-color: #ff5722 !important;
        box-shadow: 0 0 15px rgba(255, 87, 34, 0.5);
    }

    .card {
        background: rgba(20, 10, 10, 0.7);
        border: 1px solid #4a1919;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- MAP DEFINITION (Matching map.py) -----------------
_ = 0
RAW_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, 3, 3, 3, 3, _, _, _, 2, 2, 2, _, _, 1],
    [1, _, _, _, _, _, 4, _, _, _, _, _, 2, _, _, 1],
    [1, _, _, _, _, _, 4, _, _, _, _, _, 2, _, _, 1],
    [1, _, _, 3, 3, 3, 3, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, 4, _, _, _, 4, _, _, _, _, _, _, 1],
    [1, 1, 1, 3, 1, 3, 1, 1, 1, 3, _, _, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, _, _, 3, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 3, _, _, 3, 1, 1, 1],
    [1, 1, 3, 1, 1, 1, 1, 1, 1, 3, _, _, 3, 1, 1, 1],
    [1, 4, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, 2, _, _, _, _, _, 3, 4, _, 4, 3, _, 1],
    [1, _, _, 5, _, _, _, _, _, _, 3, _, 3, _, _, 1],
    [1, _, _, 2, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 1],
    [1, 4, _, _, _, _, _, _, 4, _, _, 4, _, _, _, 1],
    [1, 1, 3, 3, _, _, 3, 3, 1, 3, 3, 1, 3, 1, 1, 1],
    [1, 1, 1, 3, _, _, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 3, 3, 4, _, _, 4, 3, 3, 3, 3, 3, 3, 3, 3, 1],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, 5, _, _, _, 5, _, _, _, 5, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, _, _, _, _, _, _, _, _, _, _, _, _, _, _, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

MAP_ROWS = len(RAW_MAP)
MAP_COLS = len(RAW_MAP[0])

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("<h2 style='color:#ff5722;'>🔥 DOOM 3D FPS</h2>", unsafe_allow_html=True)
    st.markdown("**Raycasting 3D Engine & BFS AI**")
    st.markdown("Built with Python & Pygame")
    
    st.divider()
    st.markdown("### 🎮 Quick Stats")
    st.markdown("- **Engine**: 2.5D Raycaster (DDA)")
    st.markdown(f"- **Map Resolution**: {MAP_COLS} x {MAP_ROWS} tiles")
    st.markdown("- **Enemy AI**: Breadth-First Search (BFS)")
    st.markdown("- **Weapons**: Double-Barrel Shotgun")
    st.markdown("- **Monsters**: Soldier, Cacodemon, Cyberdemon")
    
    st.divider()
    st.markdown("### 🌐 Links")
    st.markdown("[⭐ View on GitHub](https://github.com/ashwanth007-d/3D-shooting-game)")
    st.markdown("[🚀 Deploy to Streamlit Cloud](https://share.streamlit.io)")
    
    st.divider()
    st.caption("Developed by **ashwanth007-d** • Streamlit Web Edition")

# ----------------- HEADER -----------------
col_title, col_stat = st.columns([3, 1])
with col_title:
    st.markdown("<div class='doom-title'>DOOM 3D FPS</div>", unsafe_allow_html=True)
    st.markdown("""
    <div>
        <span class='doom-badge'>RAYCASTING ENGINE</span>
        <span class='doom-badge'>BFS PATHFINDING</span>
        <span class='doom-badge'>PSEUDO-3D</span>
        <span class='doom-badge'>STREAMLIT READY</span>
    </div>
    """, unsafe_allow_html=True)

with col_stat:
    st.markdown("""
    <div style='background:rgba(255,87,34,0.1); border:1px solid #ff5722; padding:10px; border-radius:6px; text-align:center;'>
        <div style='font-size:0.8rem; color:#ffab91;'>STATUS</div>
        <div style='font-size:1.2rem; font-weight:bold; color:#00e676;'>ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ----------------- TABS -----------------
tabs = st.tabs([
    "🎮 Play 3D Web Game", 
    "📐 Raycasting Explorer", 
    "🧠 BFS Pathfinding AI", 
    "📸 Project Showcase & Gifs", 
    "🚀 Run Desktop / Deploy"
])

# ================= TAB 1: PLAYABLE WEB DOOM =================
with tabs[0]:
    st.markdown("### 🕹️ Interactive 3D Raycasting FPS Game")
    st.markdown("Play the 3D raycasting game directly in your browser! Controls: **WASD** to move, **Arrow Keys** or **Mouse** to look, **SPACE / Click** to fire shotgun.")

    playable_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                background-color: #0c0505;
                color: #fff;
                font-family: 'Courier New', Courier, monospace;
                display: flex;
                flex-direction: column;
                align-items: center;
                user-select: none;
                overflow: hidden;
            }}
            #game-container {{
                position: relative;
                width: 900px;
                max-width: 100%;
                box-shadow: 0 0 30px rgba(255, 60, 0, 0.4);
                border: 2px solid #b71c1c;
                border-radius: 6px;
                overflow: hidden;
            }}
            canvas {{
                display: block;
                width: 100%;
                background: #000;
                cursor: crosshair;
            }}
            #hud {{
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                background: linear-gradient(180deg, rgba(20,0,0,0.7) 0%, rgba(50,5,5,0.95) 100%);
                border-top: 2px solid #b71c1c;
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 8px 15px;
                font-family: 'Impact', sans-serif;
                letter-spacing: 2px;
                font-size: 22px;
                color: #ff3d00;
                text-shadow: 2px 2px #000;
            }}
            .hud-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .hud-label {{
                font-size: 11px;
                color: #aaa;
                letter-spacing: 1px;
            }}
            #controls-bar {{
                margin-top: 10px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                justify-content: center;
            }}
            .btn {{
                background: #b71c1c;
                color: #fff;
                border: 1px solid #ff5722;
                padding: 6px 14px;
                border-radius: 4px;
                font-size: 13px;
                cursor: pointer;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .btn:hover {{
                background: #d32f2f;
                box-shadow: 0 0 10px #ff5722;
            }}
            #instructions {{
                font-size: 12px;
                color: #ffab91;
                margin-top: 8px;
                text-align: center;
            }}
            .mobile-btn-grid {{
                display: none;
                grid-template-columns: repeat(3, 50px);
                gap: 5px;
                margin-top: 10px;
            }}
            @media (max-width: 768px) {{
                .mobile-btn-grid {{ display: grid; }}
            }}
        </style>
    </head>
    <body>
        <div id="game-container">
            <canvas id="viewport" width="800" height="480"></canvas>
            <div id="hud">
                <div class="hud-item">
                    <span class="hud-label">HEALTH</span>
                    <span id="health-val" style="color:#00e676;">100%</span>
                </div>
                <div class="hud-item">
                    <span class="hud-label">ARMOR</span>
                    <span id="armor-val" style="color:#29b6f6;">50%</span>
                </div>
                <div class="hud-item">
                    <span class="hud-label">AMMO</span>
                    <span id="ammo-val">30</span>
                </div>
                <div class="hud-item">
                    <span class="hud-label">KILLS</span>
                    <span id="kill-val">0</span>
                </div>
            </div>
        </div>

        <div id="controls-bar">
            <button class="btn" onclick="shootGun()">🔥 Fire (Space / Click)</button>
            <button class="btn" onclick="toggleAudio()" id="audio-btn">🔊 Sound: ON</button>
            <button class="btn" onclick="restartGame()">🔄 Restart Level</button>
        </div>

        <div id="instructions">
            ⌨️ <b>WASD</b>: Move | <b>Q / E or ← / →</b>: Rotate View | <b>SPACE / Click Screen</b>: Shoot Shotgun | <b>M</b>: Toggle Minimap
        </div>

        <script>
            const canvas = document.getElementById('viewport');
            const ctx = canvas.getContext('2d');
            const W = canvas.width;
            const H = canvas.height;

            // Map matching the python map
            const MAP = {RAW_MAP};
            const MAP_H = MAP.length;
            const MAP_W = MAP[0].length;

            // Audio Context for synthesized retro sound effects
            let audioCtx = null;
            let soundEnabled = true;

            function initAudio() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                }}
            }}

            function playSound(type) {{
                if (!soundEnabled) return;
                try {{
                    initAudio();
                    if (audioCtx.state === 'suspended') audioCtx.resume();
                    const now = audioCtx.currentTime;
                    
                    if (type === 'shotgun') {{
                        // Blast noise
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(140, now);
                        osc.frequency.exponentialRampToValueAtTime(30, now + 0.35);
                        gain.gain.setValueAtTime(0.5, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.35);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start(now);
                        osc.stop(now + 0.35);
                    }} else if (type === 'hit') {{
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.type = 'square';
                        osc.frequency.setValueAtTime(300, now);
                        osc.frequency.linearRampToValueAtTime(80, now + 0.2);
                        gain.gain.setValueAtTime(0.3, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start(now);
                        osc.stop(now + 0.2);
                    }} else if (type === 'roar') {{
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.type = 'sawtooth';
                        osc.frequency.setValueAtTime(80, now);
                        osc.frequency.linearRampToValueAtTime(50, now + 0.4);
                        gain.gain.setValueAtTime(0.2, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.4);
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        osc.start(now);
                        osc.stop(now + 0.4);
                    }}
                }} catch(e) {{}}
            }}

            function toggleAudio() {{
                soundEnabled = !soundEnabled;
                document.getElementById('audio-btn').innerText = soundEnabled ? "🔊 Sound: ON" : "🔇 Sound: OFF";
            }}

            // Player state
            let player = {{
                x: 1.5,
                y: 5.0,
                angle: 0.0,
                fov: Math.PI / 3,
                speed: 0.045,
                rotSpeed: 0.038,
                health: 100,
                armor: 50,
                ammo: 30,
                kills: 0
            }};

            // Enemies (Soldier, Cacodemon, Cyberdemon)
            let enemies = [
                {{ x: 4.5, y: 3.5, type: 'cacodemon', hp: 4, maxHp: 4, size: 0.6, color: '#e53935', eyeColor: '#00e5ff', dead: false, anim: 0 }},
                {{ x: 10.5, y: 3.5, type: 'soldier', hp: 3, maxHp: 3, size: 0.5, color: '#388e3c', eyeColor: '#ffeb3b', dead: false, anim: 0 }},
                {{ x: 8.5, y: 15.5, type: 'cyberdemon', hp: 8, maxHp: 8, size: 0.8, color: '#8e24aa', eyeColor: '#ff1744', dead: false, anim: 0 }},
                {{ x: 12.5, y: 20.5, type: 'soldier', hp: 3, maxHp: 3, size: 0.5, color: '#388e3c', eyeColor: '#ffeb3b', dead: false, anim: 0 }},
                {{ x: 6.5, y: 28.5, type: 'cacodemon', hp: 4, maxHp: 4, size: 0.6, color: '#e53935', eyeColor: '#00e5ff', dead: false, anim: 0 }}
            ];

            // Keys
            const keys = {{}};
            window.addEventListener('keydown', e => {{
                keys[e.key.toLowerCase()] = true;
                if (e.key === ' ' || e.code === 'Space') {{
                    e.preventDefault();
                    shootGun();
                }}
                if (['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)) {{
                    e.preventDefault();
                }}
            }});
            window.addEventListener('keyup', e => {{
                keys[e.key.toLowerCase()] = false;
            }});

            canvas.addEventListener('click', () => {{
                shootGun();
            }});

            let weaponState = {{
                firing: false,
                frame: 0,
                flashTimer: 0
            }};

            function shootGun() {{
                if (player.ammo <= 0 || weaponState.firing) return;
                player.ammo--;
                document.getElementById('ammo-val').innerText = player.ammo;
                weaponState.firing = true;
                weaponState.frame = 1;
                weaponState.flashTimer = 4;
                playSound('shotgun');

                // Check hit in center crosshair
                const aimAngle = player.angle;
                let hitDist = 999;
                let hitEnemy = null;

                enemies.forEach(en => {{
                    if (en.dead) return;
                    const dx = en.x - player.x;
                    const dy = en.y - player.y;
                    const dist = Math.hypot(dx, dy);
                    const enemyAngle = Math.atan2(dy, dx);
                    let angleDiff = enemyAngle - player.angle;
                    while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
                    while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

                    if (Math.abs(angleDiff) < 0.18 && dist < hitDist) {{
                        hitDist = dist;
                        hitEnemy = en;
                    }}
                }});

                if (hitEnemy) {{
                    hitEnemy.hp -= 2;
                    playSound('hit');
                    if (hitEnemy.hp <= 0) {{
                        hitEnemy.dead = true;
                        player.kills++;
                        document.getElementById('kill-val').innerText = player.kills;
                        playSound('roar');
                    }}
                }}
            }}

            function restartGame() {{
                player.x = 1.5;
                player.y = 5.0;
                player.angle = 0;
                player.health = 100;
                player.ammo = 30;
                player.kills = 0;
                enemies.forEach(en => {{
                    en.hp = en.maxHp;
                    en.dead = false;
                }});
                document.getElementById('health-val').innerText = "100%";
                document.getElementById('ammo-val').innerText = "30";
                document.getElementById('kill-val').innerText = "0";
            }}

            function isWall(x, y) {{
                const mx = Math.floor(x);
                const my = Math.floor(y);
                if (my < 0 || my >= MAP_H || mx < 0 || mx >= MAP_W) return 1;
                return MAP[my][mx];
            }}

            const WALL_COLORS = {{
                1: {{ light: '#8b0000', dark: '#5c0000' }},  // Red Brick
                2: {{ light: '#2e7d32', dark: '#1b5e20' }},  // Moss Stone
                3: {{ light: '#bf360c', dark: '#870000' }},  // Rust Blood
                4: {{ light: '#1565c0', dark: '#0d47a1' }},  // Tech Blue
                5: {{ light: '#f57f17', dark: '#bc5100' }}   // Demon Gold
            }};

            // Game Loop
            let showMinimap = true;

            function update() {{
                // Rotation
                if (keys['arrowleft'] || keys['q']) player.angle -= player.rotSpeed;
                if (keys['arrowright'] || keys['e']) player.angle += player.rotSpeed;

                // Movement vector
                let dx = 0;
                let dy = 0;
                const cos = Math.cos(player.angle);
                const sin = Math.sin(player.angle);

                if (keys['w'] || keys['arrowup']) {{
                    dx += cos * player.speed;
                    dy += sin * player.speed;
                }}
                if (keys['s'] || keys['arrowdown']) {{
                    dx -= cos * player.speed;
                    dy -= sin * player.speed;
                }}
                if (keys['a']) {{
                    dx += sin * player.speed;
                    dy -= cos * player.speed;
                }}
                if (keys['d']) {{
                    dx -= sin * player.speed;
                    dy += cos * player.speed;
                }}

                // Collision detection with slide
                const padding = 0.2;
                if (!isWall(player.x + dx + (dx > 0 ? padding : -padding), player.y)) {{
                    player.x += dx;
                }}
                if (!isWall(player.x, player.y + dy + (dy > 0 ? padding : -padding))) {{
                    player.y += dy;
                }}

                // Update weapon animation
                if (weaponState.firing) {{
                    weaponState.frame++;
                    if (weaponState.frame > 8) {{
                        weaponState.firing = false;
                        weaponState.frame = 0;
                    }}
                }}
                if (weaponState.flashTimer > 0) weaponState.flashTimer--;

                // Update enemies (chase player if close)
                enemies.forEach(en => {{
                    if (en.dead) return;
                    en.anim += 0.05;
                    const ex = player.x - en.x;
                    const ey = player.y - en.y;
                    const dist = Math.hypot(ex, ey);
                    if (dist > 1.2 && dist < 7) {{
                        const nx = en.x + (ex / dist) * 0.015;
                        const ny = en.y + (ey / dist) * 0.015;
                        if (!isWall(nx, ny)) {{
                            en.x = nx;
                            en.y = ny;
                        }}
                    }} else if (dist <= 1.2) {{
                        // Damage player
                        if (Math.random() < 0.03) {{
                            player.health = Math.max(0, player.health - 2);
                            document.getElementById('health-val').innerText = player.health + "%";
                            playSound('roar');
                        }}
                    }}
                }});
            }}

            function render() {{
                // 1. Draw Ceiling & Floor with gradient
                const ceilGrad = ctx.createLinearGradient(0, 0, 0, H / 2);
                ceilGrad.addColorStop(0, '#110303');
                ceilGrad.addColorStop(1, '#2c0c0c');
                ctx.fillStyle = ceilGrad;
                ctx.fillRect(0, 0, W, H / 2);

                const floorGrad = ctx.createLinearGradient(0, H / 2, 0, H);
                floorGrad.addColorStop(0, '#1c1b1b');
                floorGrad.addColorStop(1, '#080808');
                ctx.fillStyle = floorGrad;
                ctx.fillRect(0, H / 2, W, H / 2);

                // 2. Raycasting (DDA Algorithm)
                const numRays = 240;
                const halfFov = player.fov / 2;
                const deltaAngle = player.fov / numRays;
                const zBuffer = new Array(numRays);
                const rayWidth = W / numRays;

                let rayAngle = player.angle - halfFov;

                for (let r = 0; r < numRays; r++) {{
                    const sin = Math.sin(rayAngle);
                    const cos = Math.cos(rayAngle);

                    let dist = 0;
                    let hit = 0;
                    let side = 0; // 0 for vertical, 1 for horizontal
                    let wallType = 1;

                    let mapX = Math.floor(player.x);
                    let mapY = Math.floor(player.y);

                    const deltaDistX = Math.abs(1 / cos);
                    const deltaDistY = Math.abs(1 / sin);

                    let stepX, stepY, sideDistX, sideDistY;

                    if (cos < 0) {{
                        stepX = -1;
                        sideDistX = (player.x - mapX) * deltaDistX;
                    }} else {{
                        stepX = 1;
                        sideDistX = (mapX + 1.0 - player.x) * deltaDistX;
                    }}

                    if (sin < 0) {{
                        stepY = -1;
                        sideDistY = (player.y - mapY) * deltaDistY;
                    }} else {{
                        stepY = 1;
                        sideDistY = (mapY + 1.0 - player.y) * deltaDistY;
                    }}

                    // DDA loop
                    while (hit === 0 && dist < 20) {{
                        if (sideDistX < sideDistY) {{
                            sideDistX += deltaDistX;
                            mapX += stepX;
                            side = 0;
                        }} else {{
                            sideDistY += deltaDistY;
                            mapY += stepY;
                            side = 1;
                        }}

                        if (mapY >= 0 && mapY < MAP_H && mapX >= 0 && mapX < MAP_W) {{
                            if (MAP[mapY][mapX] > 0) {{
                                hit = 1;
                                wallType = MAP[mapY][mapX];
                            }}
                        }} else {{
                            hit = 1;
                            wallType = 1;
                        }}
                    }}

                    if (side === 0) {{
                        dist = (mapX - player.x + (1 - stepX) / 2) / cos;
                    }} else {{
                        dist = (mapY - player.y + (1 - stepY) / 2) / sin;
                    }}

                    // Remove fish-eye distortion
                    const correctedDist = dist * Math.cos(rayAngle - player.angle);
                    zBuffer[r] = correctedDist;

                    // Wall height projection
                    const wallHeight = Math.min(H * 2, (H / correctedDist) * 1.1);
                    const wallTop = (H / 2) - (wallHeight / 2);

                    // Shading & Colors
                    const colorData = WALL_COLORS[wallType] || WALL_COLORS[1];
                    ctx.fillStyle = side === 1 ? colorData.dark : colorData.light;

                    // Distance fog/shading
                    const fog = Math.max(0.15, 1 - (correctedDist / 14));
                    ctx.globalAlpha = fog;
                    ctx.fillRect(r * rayWidth, wallTop, rayWidth + 0.5, wallHeight);
                    ctx.globalAlpha = 1.0;

                    rayAngle += deltaAngle;
                }}

                // 3. Render Sprite Enemies (Billboarding)
                const sortedEnemies = [...enemies].map(en => {{
                    const dx = en.x - player.x;
                    const dy = en.y - player.y;
                    const dist = Math.hypot(dx, dy);
                    return {{ ...en, dist, dx, dy }};
                }}).sort((a, b) => b.dist - a.dist);

                sortedEnemies.forEach(en => {{
                    if (en.dist < 0.2 || en.dist > 18) return;

                    // Sprite direction relative to player angle
                    let spriteAngle = Math.atan2(en.dy, en.dx) - player.angle;
                    while (spriteAngle > Math.PI) spriteAngle -= Math.PI * 2;
                    while (spriteAngle < -Math.PI) spriteAngle += Math.PI * 2;

                    if (spriteAngle < -player.fov && spriteAngle > player.fov) return;

                    const screenX = (W / 2) + Math.tan(spriteAngle) * (W / 2) / Math.tan(halfFov);
                    const spriteHeight = Math.min(H * 1.8, (H / en.dist) * en.size);
                    const spriteWidth = spriteHeight;
                    const spriteTop = (H / 2) - (spriteHeight / 2);

                    const rayIdx = Math.floor((screenX / W) * numRays);
                    if (rayIdx >= 0 && rayIdx < numRays && zBuffer[rayIdx] > en.dist) {{
                        // Draw Sprite
                        ctx.save();
                        const fog = Math.max(0.2, 1 - (en.dist / 14));
                        ctx.globalAlpha = fog;

                        if (en.dead) {{
                            // Defeated pool/ashes
                            ctx.fillStyle = '#424242';
                            ctx.beginPath();
                            ctx.ellipse(screenX, (H/2) + spriteHeight*0.35, spriteWidth * 0.4, spriteHeight * 0.15, 0, 0, Math.PI * 2);
                            ctx.fill();
                        }} else {{
                            // Monster body
                            ctx.fillStyle = en.color;
                            ctx.beginPath();
                            const bob = Math.sin(en.anim) * 5;
                            ctx.arc(screenX, (H/2) + bob, spriteWidth * 0.35, 0, Math.PI * 2);
                            ctx.fill();

                            // Monster eye
                            ctx.fillStyle = en.eyeColor;
                            ctx.beginPath();
                            ctx.arc(screenX, (H/2) + bob - 4, spriteWidth * 0.12, 0, Math.PI * 2);
                            ctx.fill();

                            // Horns/Teeth
                            ctx.fillStyle = '#fff';
                            ctx.fillRect(screenX - 8, (H/2) + bob + 8, 4, 6);
                            ctx.fillRect(screenX + 4, (H/2) + bob + 8, 4, 6);

                            // Health bar
                            const barW = spriteWidth * 0.6;
                            ctx.fillStyle = '#d32f2f';
                            ctx.fillRect(screenX - barW/2, spriteTop - 8, barW, 4);
                            ctx.fillStyle = '#00e676';
                            ctx.fillRect(screenX - barW/2, spriteTop - 8, barW * (en.hp / en.maxHp), 4);
                        }}
                        ctx.restore();
                    }}
                }});

                // 4. Muzzle Flash & Screen Red Tint when Hurt
                if (weaponState.flashTimer > 0) {{
                    ctx.fillStyle = 'rgba(255, 200, 50, 0.25)';
                    ctx.fillRect(0, 0, W, H);
                }}

                // 5. Draw Double Barrel Shotgun Weapon
                const gunX = W / 2;
                const gunY = H - 30 + (weaponState.firing ? Math.sin(weaponState.frame) * 20 : 0);

                ctx.save();
                // Barrels
                ctx.fillStyle = '#37474f';
                ctx.fillRect(gunX - 28, gunY - 70, 24, 80);
                ctx.fillRect(gunX + 4, gunY - 70, 24, 80);
                ctx.fillStyle = '#1c262c';
                ctx.beginPath();
                ctx.arc(gunX - 16, gunY - 70, 10, 0, Math.PI * 2);
                ctx.arc(gunX + 16, gunY - 70, 10, 0, Math.PI * 2);
                ctx.fill();

                // Wooden Stock
                ctx.fillStyle = '#5d4037';
                ctx.fillRect(gunX - 22, gunY - 10, 44, 45);

                // Muzzle Fire Flash
                if (weaponState.firing && weaponState.frame < 3) {{
                    ctx.fillStyle = '#fff700';
                    ctx.beginPath();
                    ctx.arc(gunX - 16, gunY - 80, 25, 0, Math.PI * 2);
                    ctx.arc(gunX + 16, gunY - 80, 25, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = '#ff3d00';
                    ctx.beginPath();
                    ctx.arc(gunX, gunY - 95, 35, 0, Math.PI * 2);
                    ctx.fill();
                }}
                ctx.restore();

                // 6. Crosshair
                ctx.strokeStyle = '#00e676';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(W / 2, H / 2, 6, 0, Math.PI * 2);
                ctx.stroke();

                // 7. Mini-map (top right)
                const mmScale = 4;
                const mmX = W - (MAP_W * mmScale) - 10;
                const mmY = 10;

                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.fillRect(mmX - 2, mmY - 2, (MAP_W * mmScale) + 4, (MAP_H * mmScale) + 4);

                for (let my = 0; my < MAP_H; my++) {{
                    for (let mx = 0; mx < MAP_W; mx++) {{
                        if (MAP[my][mx] > 0) {{
                            ctx.fillStyle = '#78909c';
                            ctx.fillRect(mmX + mx * mmScale, mmY + my * mmScale, mmScale, mmScale);
                        }}
                    }}
                }}

                // Mini-map enemies
                enemies.forEach(en => {{
                    if (!en.dead) {{
                        ctx.fillStyle = en.color;
                        ctx.fillRect(mmX + en.x * mmScale - 1, mmY + en.y * mmScale - 1, 3, 3);
                    }}
                }});

                // Mini-map player
                ctx.fillStyle = '#00e676';
                ctx.fillRect(mmX + player.x * mmScale - 2, mmY + player.y * mmScale - 2, 4, 4);

                // Mini-map view cone
                ctx.strokeStyle = 'rgba(0, 230, 118, 0.6)';
                ctx.beginPath();
                ctx.moveTo(mmX + player.x * mmScale, mmY + player.y * mmScale);
                ctx.lineTo(
                    mmX + (player.x + Math.cos(player.angle - halfFov) * 6) * mmScale,
                    mmY + (player.y + Math.sin(player.angle - halfFov) * 6) * mmScale
                );
                ctx.moveTo(mmX + player.x * mmScale, mmY + player.y * mmScale);
                ctx.lineTo(
                    mmX + (player.x + Math.cos(player.angle + halfFov) * 6) * mmScale,
                    mmY + (player.y + Math.sin(player.angle + halfFov) * 6) * mmScale
                );
                ctx.stroke();
            }}

            function loop() {{
                update();
                render();
                requestAnimationFrame(loop);
            }}

            loop();
        </script>
    </body>
    </html>
    """

    components.html(playable_html, height=590)

# ================= TAB 2: RAYCASTING EXPLORER =================
with tabs[1]:
    st.markdown("### 📐 Step-by-Step Raycasting Simulation (2D Map & 3D Projection)")
    st.markdown("Interact with the parameters below to visualize how each ray sweeps across the grid, intersects walls, and forms the 3D first-person perspective.")

    c1, c2, c3 = st.columns(3)
    with c1:
        ray_count = st.slider("Number of Rays", min_value=10, max_value=80, value=30, step=5)
        fov_deg = st.slider("Field of View (Degrees)", min_value=30, max_value=110, value=60, step=5)
    with c2:
        player_rot = st.slider("Player Viewing Angle (Deg)", min_value=0, max_value=360, value=45, step=5)
        player_px = st.slider("Player X Position", min_value=1.5, max_value=14.5, value=2.5, step=0.5)
    with c3:
        player_py = st.slider("Player Y Position", min_value=1.5, max_value=29.5, value=5.5, step=0.5)
        correct_fisheye = st.checkbox("Correct Fish-Eye Distortion (cos factor)", value=True)

    # Pure Python Raycasting for simulation tab
    def cast_rays_2d(px, py, angle_rad, fov_rad, num_rays):
        half_fov = fov_rad / 2
        start_angle = angle_rad - half_fov
        step_angle = fov_rad / num_rays
        results = []

        for i in range(num_rays):
            r_angle = start_angle + i * step_angle
            sin_a = math.sin(r_angle)
            cos_a = math.cos(r_angle)
            
            # Simple ray march
            depth = 0
            hit_wall = False
            wall_type = 1
            hx, hy = px, py
            
            while depth < 16 and not hit_wall:
                depth += 0.05
                hx = px + cos_a * depth
                hy = py + sin_a * depth
                mx, my = int(hx), int(hy)
                if 0 <= my < MAP_ROWS and 0 <= mx < MAP_COLS:
                    if RAW_MAP[my][mx] > 0:
                        hit_wall = True
                        wall_type = RAW_MAP[my][mx]
                else:
                    hit_wall = True
                    break

            corr_depth = depth * math.cos(r_angle - angle_rad) if correct_fisheye else depth
            results.append((r_angle, depth, corr_depth, hx, hy, wall_type))
        return results

    ray_results = cast_rays_2d(
        player_px, player_py, 
        math.radians(player_rot), 
        math.radians(fov_deg), 
        ray_count
    )

    # Visualizer Display using HTML5 Canvas
    sim_html = f"""
    <div style="display:flex; flex-wrap:wrap; gap:15px; justify-content:center; background:#140808; padding:15px; border-radius:8px; border:1px solid #4a1919;">
        <div>
            <h4 style="color:#ffab91; margin-bottom:5px; font-family:sans-serif;">1. Top-Down 2D Grid with Cast Rays</h4>
            <canvas id="topdown" width="400" height="400" style="background:#000; border:1px solid #ff5722; border-radius:4px;"></canvas>
        </div>
        <div>
            <h4 style="color:#ffab91; margin-bottom:5px; font-family:sans-serif;">2. 3D Pseudo-Perspective Wall Slices</h4>
            <canvas id="view3d" width="400" height="400" style="background:#000; border:1px solid #ff5722; border-radius:4px;"></canvas>
        </div>
    </div>

    <script>
        const MAP = {RAW_MAP};
        const rows = {MAP_ROWS};
        const cols = {MAP_COLS};
        const px = {player_px};
        const py = {player_py};
        const pRot = {math.radians(player_rot)};
        const rays = {[(r[1], r[2], r[3], r[4], r[5]) for r in ray_results]};

        // Draw 2D
        const c2d = document.getElementById('topdown');
        const ctx2 = c2d.getContext('2d');
        const cellW = c2d.width / cols;
        const cellH = c2d.height / rows;

        for (let y=0; y<rows; y++) {{
            for (let x=0; x<cols; x++) {{
                if (MAP[y][x] > 0) {{
                    ctx2.fillStyle = '#616161';
                    ctx2.fillRect(x*cellW, y*cellH, cellW-0.5, cellH-0.5);
                }}
            }}
        }}

        // Draw rays
        ctx2.strokeStyle = 'rgba(255, 171, 145, 0.4)';
        ctx2.lineWidth = 1;
        rays.forEach(r => {{
            ctx2.beginPath();
            ctx2.moveTo(px * cellW, py * cellH);
            ctx2.lineTo(r[2] * cellW, r[3] * cellH);
            ctx2.stroke();
        }});

        // Draw player
        ctx2.fillStyle = '#00e676';
        ctx2.beginPath();
        ctx2.arc(px*cellW, py*cellH, 4, 0, Math.PI*2);
        ctx2.fill();

        // Draw 3D
        const c3d = document.getElementById('view3d');
        const ctx3 = c3d.getContext('2d');
        const w3 = c3d.width;
        const h3 = c3d.height;
        const numR = rays.length;
        const sliceW = w3 / numR;

        // Ceiling & floor
        ctx3.fillStyle = '#1b0000';
        ctx3.fillRect(0, 0, w3, h3/2);
        ctx3.fillStyle = '#111';
        ctx3.fillRect(0, h3/2, w3, h3/2);

        rays.forEach((r, idx) => {{
            const dist = r[1]; // corr_depth
            const h = Math.min(h3, (h3 / dist) * 1.5);
            const top = (h3 - h) / 2;
            const shade = Math.max(0.15, 1 - (dist / 14));
            
            ctx3.fillStyle = `rgba(230, 81, 0, ${{shade}})`;
            ctx3.fillRect(idx * sliceW, top, sliceW + 0.5, h);
        }});
    </script>
    """
    components.html(sim_html, height=480)

    st.markdown("""
    > **Mathematical Insight**:
    > In classical raycasting, raw Euclidean distance causes the edges of the screen to appear curved (the *fish-eye effect*). To eliminate this distortion, the raw distance is multiplied by the cosine of the angle offset:
    > $$d_{\\text{corrected}} = d \\cdot \\cos(\\theta_{\\text{ray}} - \\theta_{\\text{player}})$$
    """)

# ================= TAB 3: BFS PATHFINDING AI =================
with tabs[2]:
    st.markdown("### 🧠 Breadth-First Search (BFS) Enemy Navigation")
    st.markdown("The enemies use the **Breadth-First Search** algorithm from `pathfinding.py` to calculate the shortest obstacle-free route to the player in $O(V + E)$ time.")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        enemy_start_x = st.number_input("Enemy Start X", min_value=1, max_value=14, value=4)
        enemy_start_y = st.number_input("Enemy Start Y", min_value=1, max_value=30, value=3)
    with col_b2:
        player_goal_x = st.number_input("Player Target X", min_value=1, max_value=14, value=2)
        player_goal_y = st.number_input("Player Target Y", min_value=1, max_value=30, value=6)

    # Real BFS implementation matching pathfinding.py
    def run_bfs(start, goal):
        ways = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur = queue.popleft()
            if cur == goal:
                break
            
            cx, cy = cur
            for dx, dy in ways:
                nx, ny = cx + dx, cy + dy
                if 0 <= ny < MAP_ROWS and 0 <= nx < MAP_COLS:
                    if RAW_MAP[ny][nx] == 0 and (nx, ny) not in visited:
                        visited[(nx, ny)] = cur
                        queue.append((nx, ny))
        
        path = []
        if goal in visited:
            curr = goal
            while curr:
                path.append(curr)
                curr = visited[curr]
            path.reverse()
        return path, list(visited.keys())

    start_pos = (int(enemy_start_x), int(enemy_start_y))
    goal_pos = (int(player_goal_x), int(player_goal_y))
    
    # Verify open tiles
    is_start_wall = RAW_MAP[start_pos[1]][start_pos[0]] != 0
    is_goal_wall = RAW_MAP[goal_pos[1]][goal_pos[0]] != 0

    if is_start_wall or is_goal_wall:
        st.warning("⚠️ Either Enemy or Player is placed inside a wall tile! Move them to an open coordinate.")
    else:
        path, visited_nodes = run_bfs(start_pos, goal_pos)
        st.success(f"Path computed! Shortest route requires **{len(path) - 1} steps** across {len(visited_nodes)} searched grid cells.")

        # Display BFS Grid
        bfs_html = f"""
        <div style="background:#110505; padding:15px; border-radius:8px; border:1px solid #4a1919; text-align:center;">
            <canvas id="bfs-canvas" width="600" height="600" style="border:1px solid #ff5722; background:#000; border-radius:4px; max-width:100%;"></canvas>
            <div style="display:flex; justify-content:center; gap:15px; margin-top:8px; font-size:12px; color:#ffab91;">
                <span>⬛ Wall</span>
                <span style="color:#00e5ff;">🟦 Explored Frontier</span>
                <span style="color:#ffeb3b;">🟨 Shortest Path</span>
                <span style="color:#ff1744;">🔴 Enemy</span>
                <span style="color:#00e676;">🟢 Player</span>
            </div>
        </div>

        <script>
            const MAP = {RAW_MAP};
            const rows = {MAP_ROWS};
            const cols = {MAP_COLS};
            const path = {path};
            const visited = {visited_nodes};
            const start = {list(start_pos)};
            const goal = {list(goal_pos)};

            const cv = document.getElementById('bfs-canvas');
            const ctx = cv.getContext('2d');
            const cw = cv.width / cols;
            const ch = cv.height / rows;

            // Draw map
            for (let y=0; y<rows; y++) {{
                for (let x=0; x<cols; x++) {{
                    ctx.fillStyle = MAP[y][x] > 0 ? '#424242' : '#141414';
                    ctx.fillRect(x*cw, y*ch, cw-0.5, ch-0.5);
                }}
            }}

            // Draw visited nodes
            ctx.fillStyle = 'rgba(0, 229, 255, 0.25)';
            visited.forEach(pt => {{
                ctx.fillRect(pt[0]*cw, pt[1]*ch, cw-0.5, ch-0.5);
            }});

            // Draw path
            ctx.strokeStyle = '#ffeb3b';
            ctx.lineWidth = 3;
            ctx.beginPath();
            path.forEach((pt, i) => {{
                const px = pt[0]*cw + cw/2;
                const py = pt[1]*ch + ch/2;
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }});
            ctx.stroke();

            // Draw Start & Goal markers
            ctx.fillStyle = '#ff1744';
            ctx.beginPath();
            ctx.arc(start[0]*cw + cw/2, start[1]*ch + ch/2, cw*0.4, 0, Math.PI*2);
            ctx.fill();

            ctx.fillStyle = '#00e676';
            ctx.beginPath();
            ctx.arc(goal[0]*cw + cw/2, goal[1]*ch + ch/2, cw*0.4, 0, Math.PI*2);
            ctx.fill();
        </script>
        """
        components.html(bfs_html, height=660)

# ================= TAB 4: PROJECT SHOWCASE & GIFS =================
with tabs[3]:
    st.markdown("### 📸 Project Gallery & Animations")
    st.markdown("Screenshots and animated captures from the desktop DOOM engine demonstration.")

    def render_responsive_image(img_path, img_caption):
        try:
            st.image(img_path, caption=img_caption, width="stretch")
        except TypeError:
            st.image(img_path, caption=img_caption, use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        if os.path.exists("photos/gameplay_1.gif"):
            render_responsive_image("photos/gameplay_1.gif", "1. Full Gameplay Demo (Pygame)")
        if os.path.exists("photos/raycast_1.gif"):
            render_responsive_image("photos/raycast_1.gif", "3. 2D Raycasting Field-of-View Sweep")
        if os.path.exists("photos/player_enemy_2.gif"):
            render_responsive_image("photos/player_enemy_2.gif", "5. BFS Enemy Pathfinding in Action")
    with g2:
        if os.path.exists("photos/weapon_1.gif"):
            render_responsive_image("photos/weapon_1.gif", "2. Weapon Recoil & Muzzle Animation")
        if os.path.exists("photos/player_1.gif"):
            render_responsive_image("photos/player_1.gif", "4. 2D Collision & Movement Verification")
        if os.path.exists("photos/gameplay_2.gif"):
            render_responsive_image("photos/gameplay_2.gif", "6. Demon Encounters & Combat")

    st.markdown("---")
    st.markdown("#### 👾 Enemy Sprite Sheets")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.markdown("**Soldier**")
        if os.path.exists("photos/soldier_1.gif"):
            st.image("photos/soldier_1.gif", width=120)
    with e2:
        st.markdown("**Caco Demon**")
        if os.path.exists("photos/cacodemon_1.gif"):
            st.image("photos/cacodemon_1.gif", width=120)
    with e3:
        st.markdown("**Cyber Demon**")
        if os.path.exists("photos/cyberdemon_1.gif"):
            st.image("photos/cyberdemon_1.gif", width=120)

# ================= TAB 5: RUN DESKTOP / DEPLOY =================
with tabs[4]:
    st.markdown("### 🚀 How to Deploy on Streamlit Community Cloud")
    st.markdown("""
    This project is ready to be hosted for free on **Streamlit Community Cloud** with one click!

    #### 1. Fork or Push Repository
    Ensure the latest version of this repo is pushed to your GitHub account:
    `https://github.com/ashwanth007-d/3D-shooting-game`

    #### 2. Connect to Streamlit
    1. Visit [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
    2. Click the **"New app"** or **"Deploy an app"** button.
    3. Fill in the details:
       - **Repository**: `ashwanth007-d/3D-shooting-game`
       - **Branch**: `main`
       - **Main file path**: `app.py`
    4. Click **Deploy!**

    ---
    ### 💻 Running Locally (Desktop Pygame Version)
    To run the native desktop Pygame application on your local machine:
    ```bash
    # 1. Clone repository
    git clone https://github.com/ashwanth007-d/3D-shooting-game.git
    cd 3D-shooting-game

    # 2. Install dependencies
    pip install pygame streamlit numpy Pillow

    # 3. Launch native desktop game
    python main.py

    # 4. Or launch this Streamlit web interface locally
    streamlit run app.py
    ```
    """)
