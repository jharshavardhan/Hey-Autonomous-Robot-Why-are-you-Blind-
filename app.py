"""
Hey Autonomous Vacuum Cleaner! Why Are You Blind?
Streamlit Simulation — Full Implementation with BFS + A*, Mapping, & Charging
"""

import streamlit as st
import time
import random

from constants import ROWS, COLS, CELL_CHARGER, CELL_OBSTACLE, CELL_EMPTY, CELL_CLEANED, FLOOR_TYPES, OBSTACLE_TYPES, ALGORITHMS
from state import VacuumState, make_grid, coverage
from simulation import step_vacuum
from render import render_grid

# --- Streamlit Application ---

st.set_page_config(page_title="Hey Autonomous Vacuum! Why Are You Blind?", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[data-testid="stAppViewContainer"]{background:#0f0f14;color:#e8e8f0;font-family:'DM Sans',sans-serif}
[data-testid="stSidebar"]{background:#16161e;border-right:0.5px solid #2a2a3a}
h1,h2,h3{font-family:'Space Mono',monospace;color:#e8e8f0}
div[data-testid="stButton"] button{font-family:'DM Sans',sans-serif;border-radius:8px}
.metric-card{background:#1e1e2a;border:0.5px solid #2a2a3a;border-radius:10px;padding:12px 16px;margin-bottom:8px}
.metric-label{font-size:11px;color:#7070a0;margin-bottom:2px}
.metric-val{font-family:'Space Mono',monospace;font-size:20px}
.log-box{background:#111118;border:0.5px solid #2a2a3a;border-radius:8px;padding:10px;height:140px;overflow-y:auto;font-family:'Space Mono',monospace;font-size:10px;color:#7070a0;line-height:1.5}
.badge{display:inline-block;padding:3px 10px;border-radius:6px;font-family:'Space Mono',monospace;font-size:11px;font-weight:700;margin-right:6px}
.bg{background:rgba(0,229,160,.15);color:#00e5a0}
.by{background:rgba(255,193,7,.15);color:#ffc107}
.bb{background:rgba(56,189,248,.15);color:#38bdf8}
.br{background:rgba(255,124,92,.15);color:#ff7c5c}
.bv{background:rgba(108,99,255,.2);color:#6c63ff}
</style>
""", unsafe_allow_html=True)

def init():
    if "grid" not in st.session_state: st.session_state.grid = make_grid()
    if "vs" not in st.session_state: st.session_state.vs = VacuumState()
    if "obs_dict" not in st.session_state: st.session_state.obs_dict = {}
    if "auto_run" not in st.session_state: st.session_state.auto_run = False

init()
_grid = st.session_state.grid
_vs   = st.session_state.vs

with st.sidebar:
    st.markdown("## 🗺️ Environment")
    floor = st.selectbox("Floor Type (Affects Sensors & Battery)", list(FLOOR_TYPES.keys()))
    fi = FLOOR_TYPES[floor]
    st.caption(fi['desc'])
    
    st.markdown("## 🧭 AI Engine")
    algo = st.selectbox("Algorithm", ALGORITHMS)
    st.info("Hybrid Mapping dynamically senses obstacles, remembers them, and paths to remaining dirt or base using BFS/A*.")
    speed = st.slider("Simulation Speed", 1, 25, 10)

    st.markdown("## 🪑 Dynamic Obstacles")
    obs_type = st.selectbox("Type", list(OBSTACLE_TYPES.keys()))
    c1, c2 = st.columns(2)
    with c1: obs_r = st.number_input("Row", 1, ROWS-2, 5)
    with c2: obs_c = st.number_input("Col", 1, COLS-2, 10)

    bc1, bc2 = st.columns(2)
    with bc1:
        if st.button("➕ Drop Object", use_container_width=True):
            r, c = int(obs_r), int(obs_c)
            # Make sure not placing on vacuum, charger, etc.
            if not (r == _vs.row and c == _vs.col) and not _grid[r, c] == CELL_CHARGER:
                _grid[r, c] = CELL_OBSTACLE
                st.session_state.obs_dict[(r, c)] = obs_type
                _vs.add_log(f"Dynamic {obs_type} dropped at {r},{c}!")
                st.rerun()
    with bc2:
        if st.button("⚡ Randomize", use_container_width=True):
            for _ in range(15):
                r, c = random.randint(2, ROWS-3), random.randint(2, COLS-3)
                if _grid[r, c] == CELL_EMPTY:
                    _grid[r, c] = CELL_OBSTACLE
                    st.session_state.obs_dict[(r, c)] = random.choice(list(OBSTACLE_TYPES.keys()))
            st.rerun()

# Layout
st.markdown("<h1>🤖 Hey Autonomous Vacuum! Why Are You Blind?</h1>", unsafe_allow_html=True)

cov = coverage(_grid)
if _vs.done: sc = "br"; text = "DONE"
elif _vs.mode == "CHARGING": sc = "by"; text = "CHARGING"
elif st.session_state.auto_run: sc = "bb"; text = "AUTO"
else: sc = "bg"; text = "IDLE"

st.markdown(f"""
<div style='margin-bottom:10px'>
  <span class='badge {sc}'>{text}</span>
  <span class='badge bb'>{floor.upper()}</span>
  <span class='badge bg'>{algo.split(" ")[0]}</span>
  <span style='font-size:12px;color:#7070a0'>Cleaned: <b style='color:#00e5a0'>{cov:.1f}%</b></span>
  {'<span style="font-size:12px;color:#ff7c5c;margin-left:12px">⚠️ ' + _vs.done_reason + '</span>' if _vs.done else ''}
</div>""", unsafe_allow_html=True)

left, right = st.columns([3, 1])

with left:
    st.markdown(render_grid(_grid, _vs, st.session_state.obs_dict), unsafe_allow_html=True)
    st.caption("⬛ Dirty &nbsp; 🟩 Cleaned &nbsp; ⚡ Charger &nbsp; 🔴 Obstacle &nbsp; 🔵 Sensor / Path")

    cc = st.columns(4)
    with cc[0]:
        if st.button("⏯ Play / Pause", use_container_width=True, type="primary"):
            st.session_state.auto_run = not st.session_state.auto_run
            if st.session_state.auto_run:
                _vs.running = True
            st.rerun()
    with cc[1]:
        if st.button("⏭ Step", use_container_width=True):
            if not _vs.done:
                step_vacuum(_grid, _vs, floor, algo)
            st.rerun()
    with cc[2]:
        if st.button("↺ Reset Vacuum", use_container_width=True):
            # Resets vacuum, makes room dirty again, but KEEPS obstacles
            st.session_state.vs = VacuumState()
            st.session_state.auto_run = False
            for r in range(ROWS):
                for c in range(COLS):
                    if _grid[r, c] == CELL_CLEANED:
                        _grid[r, c] = CELL_EMPTY
            st.rerun()
    with cc[3]:
        if st.button("🗑️ Reset All", use_container_width=True):
            # Completely purges vacuum state & grid
            st.session_state.grid = make_grid()
            st.session_state.vs = VacuumState()
            st.session_state.obs_dict = {}
            st.session_state.auto_run = False
            st.rerun()

    log_html = "".join(f"<div style='color:{'#ffc107' if 'Recharg' in l or 'Dock' in l else '#00e5a0' if 'Clean' in l else '#ff7c5c' if 'stacle' in l or 'terminat' in l.lower() else '#38bdf8'}'>{l}</div>" for l in reversed(_vs.log[-15:]))
    st.markdown(f"<div class='log-box'>{log_html}</div>", unsafe_allow_html=True)

with right:
    b_color = "#00e5a0" if _vs.battery > 50 else ("#ffc107" if _vs.battery > 20 else "#ff7c5c")
    st.markdown(f"""
    <div class='metric-card'><div class='metric-label'>Coverage</div><div class='metric-val' style='color:#00e5a0'>{cov:.1f}%</div></div>
    <div class='metric-card'><div class='metric-label'>Battery</div><div class='metric-val' style='color:{b_color}'>{_vs.battery:.0f}%</div></div>
    <div class='metric-card'><div class='metric-label'>Mode</div><div class='metric-val' style='color:#38bdf8'>{_vs.mode}</div></div>
    <div class='metric-card'><div class='metric-label'>Obstacle Hits</div><div class='metric-val' style='color:#ff7c5c'>{_vs.hits}</div></div>
    <div class='metric-card'><div class='metric-label'>Steps Taken</div><div class='metric-val' style='color:#7070a0'>{_vs.steps}</div></div>
    """, unsafe_allow_html=True)

# Controls Logic is now handled entirely inside the buttons above.
# We just need to handle the auto run loop here.

if st.session_state.auto_run and not _vs.done:
    # Scale simulation speed based on floor type
    actual_speed = speed
    if floor == "Carpet":
        actual_speed = max(1, speed // 2)
    elif floor == "Tile":
        actual_speed = int(speed * 1.5)

    for _ in range(actual_speed):
        if _vs.done: break
        step_vacuum(_grid, _vs, floor, algo)
    time.sleep(0.04)
    st.rerun()