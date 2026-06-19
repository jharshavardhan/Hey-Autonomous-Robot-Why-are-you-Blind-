import random
import numpy as np

from constants import ROWS, COLS, CELL_VACUUM, CELL_WALL, CELL_OBSTACLE, CELL_EMPTY, CELL_CLEANED, CELL_UNKNOWN, FLOOR_TYPES
from state import VacuumState, coverage
from pathfinding import heuristic, a_star, find_nearest_target

# --- Step Simulation Controller ---

def step_vacuum(grid: np.ndarray, vs: VacuumState, floor: str, algo: str):
    if vs.done: return
    
    # Floor type properties
    battery_drain = FLOOR_TYPES[floor]["drain"]
    eff = FLOOR_TYPES[floor]["efficiency"]
    sensor_acc = FLOOR_TYPES[floor]["sensor_acc"]
    
    # Floor-based Movement Reality Check
    if floor == "Carpet" and random.random() < 0.25:
        # Carpet is thick; 25% chance the vacuum struggles and takes a tick to just push through without moving
        vs.steps += 1
        vs.battery = max(0.0, vs.battery - battery_drain)
        if vs.battery <= 0:
            vs.done = True
            vs.done_reason = "Battery dead!"
        return

    # 1. Simulate Sensors (Update Internal Map dynamically)
    obstacle_detected = False
    for r in range(max(0, vs.row - 2), min(ROWS, vs.row + 3)):
        for c in range(max(0, vs.col - 2), min(COLS, vs.col + 3)):
            actual_state = grid[r, c]
            if actual_state != CELL_VACUUM and vs.internal_map[r, c] != actual_state:
                # Sensor realism: if it's an obstacle on carpet, sensor might fail to register it immediately
                if actual_state == CELL_OBSTACLE:
                    if random.random() < sensor_acc:
                        vs.internal_map[r, c] = actual_state
                        obstacle_detected = True
                else:
                    vs.internal_map[r, c] = actual_state

    # Trigger re-planning if path is blocked by a newly sensed dynamic obstacle
    if obstacle_detected and vs.path:
        for pr, pc in vs.path:
            if vs.internal_map[pr, pc] == CELL_OBSTACLE:
                # We saw an obstacle on our intended path! 
                # Simulate delay: clear path now so it re-plans on the next tick
                vs.path = []
                vs.add_log("Sensor spotted obstacle on path! Re-planning...")
                break

    # 2. Battery & Charging Logic
    dist_to_charger = heuristic((vs.row, vs.col), vs.charger_pos)
    
    if vs.battery < (dist_to_charger * battery_drain) + 5.0 and vs.mode != "CHARGING":
        if vs.mode != "RETURNING":
            vs.mode = "RETURNING"
            vs.add_log("Low battery! Returning to dock.")
            vs.path = [] # force re-plan
            
    if vs.mode == "CHARGING":
        vs.battery = min(100.0, vs.battery + 8.0)
        if vs.battery >= 100.0:
            vs.mode = "EXPLORING"
            vs.add_log("Recharged! Resuming cleaning.")
            vs.path = []
        return # Skip movement while charging

    # 3. Path Planning & Movement
    moved = False

    if "Hybrid Smart Mapping" in algo:
        if vs.mode == "RETURNING":
            if (vs.row, vs.col) == vs.charger_pos:
                vs.mode = "CHARGING"
                vs.add_log("Docked. Recharging...")
                return
            if not vs.path:
                vs.path = a_star((vs.row, vs.col), vs.charger_pos, vs.internal_map)
                if not vs.path:
                    vs.done = True
                    vs.done_reason = "Trapped, can't reach base!"
                    return

        elif vs.mode == "EXPLORING":
            if not vs.path:
                # Use BFS to find shortest path to nearest dirty block
                vs.path = find_nearest_target(vs, [CELL_EMPTY, CELL_UNKNOWN])
                if not vs.path:
                    vs.mode = "RETURNING"
                    vs.path = a_star((vs.row, vs.col), vs.charger_pos, vs.internal_map)
                    vs.add_log("Room cleaned! Returning to base.")
                    if not vs.path and (vs.row, vs.col) != vs.charger_pos:
                        vs.done = True
                        vs.done_reason = "Cleaned, but base blocked."
                    return

        # Execute next step in Path
        if vs.path:
            nr, nc = vs.path[0]
            # Collision detection (Sensor might have missed it, but bumper hit it)
            if grid[nr, nc] in (CELL_WALL, CELL_OBSTACLE):
                vs.hits += 1
                vs.internal_map[nr, nc] = grid[nr, nc] # Force update map on bump
                vs.path = [] # Clear path to trigger rebuild next turn
                vs.add_log("Bumper hit obstacle! Re-routing...")
            else:
                vs.row, vs.col = nr, nc
                vs.path.pop(0)
                moved = True

    elif "DFS" in algo:
        if not vs.visited:
            vs.visited.add((vs.row, vs.col))
            
        neighbors = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = vs.row + dr, vs.col + dc
            if 1 <= nr < ROWS - 1 and 1 <= nc < COLS - 1:
                if (nr, nc) not in vs.visited and grid[nr, nc] not in (CELL_WALL, CELL_OBSTACLE):
                    neighbors.append((nr, nc))
                    
        if neighbors:
            # Pick first available neighbor to explore deeper
            nr, nc = neighbors[0]
            vs.visited.add((nr, nc))
            vs.dfs_stack.append((vs.row, vs.col)) # Push current position for backtracking
            vs.row, vs.col = nr, nc
            moved = True
        else:
            # Backtrack
            if vs.dfs_stack:
                nr, nc = vs.dfs_stack.pop()
                if grid[nr, nc] not in (CELL_WALL, CELL_OBSTACLE):
                    vs.row, vs.col = nr, nc
                    moved = True
                    vs.add_log("DFS Backtracking...")
                else:
                    vs.add_log("DFS backtrack path blocked!")
                    vs.hits += 1
            else:
                vs.done = True
                vs.done_reason = "DFS Exploration complete (no more accessible space)."

    elif "Greedy" in algo:
        target = None
        min_dist = float('inf')
        
        # Greedy heuristic: Find the absolute closest unknown or empty cell
        for r in range(1, ROWS - 1):
            for c in range(1, COLS - 1):
                if vs.internal_map[r, c] in (CELL_EMPTY, CELL_UNKNOWN):
                    d = heuristic((vs.row, vs.col), (r, c))
                    if d < min_dist and d > 0:
                        min_dist = d
                        target = (r, c)
                        
        if target:
            # Evaluate all valid immediate neighbors and pick the one closest to target
            best_neighbor = None
            best_d = float('inf')
            
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = vs.row + dr, vs.col + dc
                if 1 <= nr < ROWS - 1 and 1 <= nc < COLS - 1:
                    if grid[nr, nc] not in (CELL_WALL, CELL_OBSTACLE):
                        d = heuristic((nr, nc), target)
                        # To try to break local minima (getting trapped in corners), we add a tiny bit of random jitter 
                        # if multiple paths have similar cost, or we just strictly pick the best. Let's do strict greedy.
                        if d < best_d:
                            best_d = d
                            best_neighbor = (nr, nc)
                            
            if best_neighbor:
                vs.row, vs.col = best_neighbor
                moved = True
            else:
                vs.hits += 1
                vs.add_log("Greedy is stuck in a corner.")
        else:
            vs.done = True
            vs.done_reason = "Greedy Search found no remaining dirty spots."

    # 4. Clean logic
    if grid[vs.row, vs.col] == CELL_EMPTY:
        if random.random() < eff:
            grid[vs.row, vs.col] = CELL_CLEANED
            vs.internal_map[vs.row, vs.col] = CELL_CLEANED
            vs.cleaned += 1
        else:
            vs.skipped += 1

    # Updates
    if moved:
        vs.steps += 1
        vs.battery = max(0.0, vs.battery - battery_drain)
        
    if vs.battery <= 0:
        vs.done = True
        vs.done_reason = "Battery dead out in the field!"
        vs.add_log("Battery died before reaching base")
        return

    # Check Victory Condition
    current_cov = coverage(grid)
    if current_cov >= 99.9 and (vs.row, vs.col) == vs.charger_pos:
        vs.done = True
        vs.done_reason = "Fully Cleaned & Docked!"
        vs.add_log(f"Success! {vs.cleaned} cells cleaned in {vs.steps} steps")

    # Check Termination for blind algorithms
    if "Smart Mapping" not in algo:
        if vs.steps > vs.max_steps:
             vs.done = True
             vs.done_reason = "Max steps limit reached."
        if current_cov > vs.last_coverage:
            vs.last_coverage = current_cov
            vs.no_progress_steps = 0
        else:
            vs.no_progress_steps += 1
            
        if vs.no_progress_steps > 150:
            vs.done = True
            vs.done_reason = "Trapped. No cleaning progress in 150 steps."
            vs.add_log("Simulation terminated due to lack of progress.")
