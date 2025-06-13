#non-contextual ucb
"""
noncontextual_ucb.py
--------------------
A simple UCB-1 (context-free) policy over K arms.

At each time step t=1,2,…:
  • If any arm i has never been pulled yet, pull it once.
  • Otherwise, compute for each arm i:
        p_i(t) = μ̂_i + sqrt( (2 * ln t) / n_i )
    where
        μ̂_i = observed average reward of arm i so far,
        n_i  = number of times arm i was pulled so far.
    and pick arm = argmax p_i(t)  (break ties randomly).

  • After observing reward r, update:
        n_i ← n_i + 1
        sum_i ← sum_i + r
        μ̂_i = sum_i / n_i
"""

import numpy as np
import random
from typing import List


class NonContextualUCB:
    """Simple UCB-1 bandit over K arms, no contextual features."""

    def __init__(self, n_arms: int, seed: int):
        self.n_arms = n_arms
        self.counts: List[int] = [0] * n_arms     # n_i = times arm i pulled
        self.sums:   List[float] = [0.0] * n_arms  # sum of rewards for arm i
        if seed is None:
            self.rng = random.Random()
        else:
            self.rng = random.Random(seed)

    def select_arm(self, t: int) -> int:
        """
        Return an arm index in {0,…,n_arms-1} to pull at time t (1-based).
        If any arm i has counts[i]==0, return that arm (initialization).
        Otherwise compute UCB score for each arm and return the argmax.
        """
        # 1) If any arm hasn't been pulled yet, pull it once
        for i in range(self.n_arms):
            if self.counts[i] == 0:
                return i

        # 2) All arms have been seen at least once → compute UCB scores
        ucb_values = [0.0] * self.n_arms
        log_t = np.log(t)
        for i in range(self.n_arms):
            mean_i = self.sums[i] / self.counts[i]                  # μ̂_i
            bonus  = np.sqrt((2 * log_t) / self.counts[i])         # sqrt((2 ln t)/n_i)
            ucb_values[i] = mean_i + bonus

        # 3) break ties randomly
        max_val = max(ucb_values)
        best_arms = [i for i, v in enumerate(ucb_values) if v == max_val]
        return self.rng.choice(best_arms)

    def update(self, arm_idx: int, reward: float):
        """
        Update counts & sums after pulling arm_idx and observing reward.
        """
        self.counts[arm_idx] += 1
        self.sums[arm_idx] += reward

    def reset(self):
        """Reset the policy to zero pulls (if you want to reuse)."""
        self.counts = [0] * self.n_arms
        self.sums   = [0.0] * self.n_arms