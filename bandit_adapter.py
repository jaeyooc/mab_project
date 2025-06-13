"""
bandit_adapter.py

Provides a thin wrapper so you can plug NonContextualUCB into the same
simulation loop that expects LinUCBPolicy.
"""

from typing import Any
import numpy as np
from src.noncontextual_ucb import NonContextualUCB


class UCBPolicyAdapter:
    """
    Adapter that makes NonContextualUCB look like a 3-argument policy:
       select_arm(ctx: np.ndarray) -> int
       update(arm_idx: int, reward: float, ctx: np.ndarray) -> None
    Internally ignores ctx and just counts t internally.
    """

    def __init__(self, n_arms: int, seed: int):
        self.ucb = NonContextualUCB(n_arms=n_arms, seed=seed)
        self.time = 1  # will increment on each call to select_arm

    def select_arm(self, ctx: Any = None):
        """
        The simulation will pass `ctx` (the context vector), but UCB1 ignores it.
        We only need to pass `self.time` to choose an arm.
        """
        arm = self.ucb.select_arm(self.time)
        # increment time for the next round
        self.time += 1
        return arm

    def update(self, arm_idx: int, reward: float, ctx: Any = None) -> None:
        """
        The simulation will call update(arm_idx, reward, ctx). We ignore ctx for UCB.
        """
        self.ucb.update(arm_idx, reward)
