#linucb_policy.py

from __future__ import annotations
import numpy as np
from typing import List
from src.linucb_arm import LinUCBDisjointArm

class LinUCBPolicy:
    """ DIsjoint LinUCB with K independent arms"""

    def __init__ (self, n_arms, dim, alpha):
        self.arms: List[LinUCBDisjointArm] = [
            LinUCBDisjointArm(i, dim, alpha) for i in range(n_arms)
        ]
        self.rng = np.random.default_rng() #for tie breaker: select randomly

    # ------------------------------------------------------------------ #
    # Arm selection with random tie-break
    # ------------------------------------------------------------------ #
    def select_arm(self, x:np.ndarray) -> int:
        p_vals = [arm.ucb(x) for arm in self.arms]
        best = np.argwhere(p_vals == np.max(p_vals)).flatten()
        return int(self.rng.choice(best))
    
    def update(self, arm_idx:int, reward: float, x:np.ndarray) -> None:
        self.arms[arm_idx].update(reward,x)