import numpy as np

from constants import ROWS, COLS, CELL_VACUUM, CELL_CHARGER, CELL_WALL, CELL_OBSTACLE, CELL_CLEANED, OBSTACLE_TYPES
from state import VacuumState

# --- Grid Renderer ──────────────────────────────────────

def render_grid(grid: np.ndarray, vs: VacuumState, obs_dict: dict) -> str:
    display = grid.copy()
    display[vs.row, vs.col] = CELL_VACUUM
    
    path_set = set(vs.path) if vs.path else set()

    html = [f"<div style='display: grid; grid-template-columns: repeat({COLS}, 1fr); grid-template-rows: repeat({ROWS}, 1fr); gap: 1px; background-color: #1a1a2a; border: 1px solid #2a2a3a; border-radius: 6px; padding: 4px; width: 100%; aspect-ratio: {COLS}/{ROWS};'>"]
    
    for r in range(ROWS):
        for c in range(COLS):
            v = int(display[r, c])
            dist = max(abs(r - vs.row), abs(c - vs.col))
            is_sensor = (1 <= dist <= 2 and v not in (CELL_WALL, CELL_OBSTACLE, CELL_VACUUM, CELL_CHARGER))
            is_path = (r, c) in path_set
            
            char = ""
            color = "#2a2010" # Default dirty
            
            if v == CELL_VACUUM:
                color = "#00e5a0"
                if vs.mode == "CHARGING": char = "🔌"
                else: char = "🤖"
            elif v == CELL_CHARGER:
                color = "#ffc107"
                char = "⚡"
            elif v == CELL_WALL:
                color = "#14141c"
            elif v == CELL_OBSTACLE:
                obs_t = obs_dict.get((r, c))
                color = OBSTACLE_TYPES.get(obs_t, "#3a2525") if obs_t else "#3a2525"
            elif v == CELL_CLEANED:
                color = "#1a3a1a" # Clean
            elif is_sensor:
                color = "#0a2030" # Sensor range
            
            # Show small dot for path if it's empty, cleaned, or sensor
            if is_path and v not in (CELL_VACUUM, CELL_CHARGER, CELL_WALL, CELL_OBSTACLE):
                char = "•"
                if color == "#2a2010": color = "#1a3020"
                elif color == "#0a2030": color = "#0a4040"
                elif color == "#1a3a1a": color = "#1a5a3a"

            html.append(f"<div style='background-color: {color}; display: flex; align-items: center; justify-content: center; font-size: min(1.5vw, 16px); line-height: 1; user-select: none; border-radius: 2px;'>{char}</div>")
            
    html.append("</div>")
    return "".join(html)
