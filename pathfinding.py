import heapq
from collections import deque
from typing import List, Tuple
import numpy as np

from constants import ROWS, COLS, CELL_WALL, CELL_OBSTACLE
from state import VacuumState

# --- Pathfinding (A* and BFS) ---

def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start: Tuple[int, int], goal: Tuple[int, int], internal_map: np.ndarray) -> List[Tuple[int, int]]:
    """A* algorithm to find shortest path to a specific goal avoiding known obstacles."""
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
            
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS:
                # Do not move through known walls or obstacles
                if internal_map[neighbor[0], neighbor[1]] in (CELL_WALL, CELL_OBSTACLE):
                    continue
            else:
                continue
                
            tentative_g_score = gscore[current] + 1
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
                
    return [] # No path

def find_nearest_target(vs: VacuumState, target_types: List[int]) -> List[Tuple[int, int]]:
    """Breadth-First Search to find the nearest cell matching any of the target types."""
    queue = deque([(vs.row, vs.col, [])])
    visited = set([(vs.row, vs.col)])
    
    while queue:
        r, c, path = queue.popleft()
        
        # If we found a target, return the path
        if vs.internal_map[r, c] in target_types and (r != vs.row or c != vs.col):
            return path
            
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in visited:
                if vs.internal_map[nr, nc] not in (CELL_WALL, CELL_OBSTACLE):
                    visited.add((nr, nc))
                    queue.append((nr, nc, path + [(nr, nc)]))
    return []
