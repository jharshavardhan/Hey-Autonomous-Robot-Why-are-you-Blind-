# --- Grid Constants ---
ROWS, COLS = 20, 28
CELL_UNKNOWN  = -1  # Used by vacuum's internal map
CELL_EMPTY    = 0   # Dirty floor
CELL_WALL     = 1
CELL_OBSTACLE = 2
CELL_CLEANED  = 3
CELL_VACUUM   = 4
CELL_CHARGER  = 5

# --- Environment Configurations ---
FLOOR_TYPES = {
    "Hardwood": {"efficiency": 0.95, "sensor_acc": 0.95, "drain": 0.15, "desc": "Standard speed. Good traction, reliable cleaning."},
    "Carpet":   {"efficiency": 0.70, "sensor_acc": 0.50, "drain": 0.35, "desc": "Slow movement. Weak sensors, requires multiple passes (70% clean rate), heavy drain."},
    "Tile":     {"efficiency": 0.88, "sensor_acc": 0.85, "drain": 0.10, "desc": "Fast movement. Grout traps dirt (88% clean rate). Very low battery drain."},
}

OBSTACLE_TYPES = {
    "Chair legs": "#a0522d",
    "Table":      "#8b6914",
    "Toy":        "#d63384",
    "Cable":      "#0d6efd",
    "Pet bowl":   "#198754",
    "Shoe":       "#6f42c1",
    "Wall block": "#495057",
}

ALGORITHMS = ["Hybrid Smart Mapping (BFS + A*)", "DFS Exploration", "Greedy Search (Nearest Dirt)"]
