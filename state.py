import time
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Set

from constants import (
    ROWS, COLS, CELL_UNKNOWN, CELL_WALL, CELL_CHARGER, 
    CELL_OBSTACLE, CELL_CLEANED
)

# --- Vacuum State & Agent properties ---
@dataclass
class VacuumState:
    row: int = 1
    col: int = 1
    direction: int = 1
    spiral_side: int = 0
    steps: int = 0
    hits: int = 0
    cleaned: int = 0
    skipped: int = 0
    battery: float = 100.0
    log: List[str] = field(default_factory=list)
    running: bool = False
    done: bool = False
    done_reason: str = ""
    
    # Internal map & A* state (What the vacuum "knows")
    internal_map: np.ndarray = field(default_factory=lambda: np.full((ROWS, COLS), CELL_UNKNOWN))
    path: List[Tuple[int, int]] = field(default_factory=list)
    charger_pos: Tuple[int, int] = (1, 1)
    mode: str = "EXPLORING"  # EXPLORING, RETURNING, CHARGING

    # Termination Trackers
    max_steps: int = 1800
    no_progress_steps: int = 0
    last_coverage: float = 0.0

    # For DFS
    dfs_stack: List[Tuple[int, int]] = field(default_factory=list)
    visited: Set[Tuple[int, int]] = field(default_factory=set)

    def add_log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        self.log.append(f"[{ts}] {msg}")
        if len(self.log) > 120:
            self.log = self.log[-120:]

def make_grid() -> np.ndarray:
    g = np.zeros((ROWS, COLS), dtype=int)
    # Surround with walls
    g[0, :] = CELL_WALL
    g[-1, :] = CELL_WALL
    g[:, 0] = CELL_WALL
    g[:, -1] = CELL_WALL
    # Place charging dock
    g[1, 1] = CELL_CHARGER
    return g

def obstacle_count(grid: np.ndarray) -> int:
    return int((grid == CELL_OBSTACLE).sum())

def coverage(grid: np.ndarray) -> float:
    # Everything except walls, obstacles, and charger is cleanable
    cleanable = (ROWS - 2) * (COLS - 2) - obstacle_count(grid) - 1 # -1 for charger
    if cleanable <= 0:
        return 100.0
    cleaned = int((grid == CELL_CLEANED).sum())
    return min(100.0, cleaned / cleanable * 100)
