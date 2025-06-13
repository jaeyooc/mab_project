#!/usr/bin/env python
"""
cli_online.py – balanced per-persona runner
"""
from __future__ import annotations
import argparse
from pathlib import Path

from .linucb_policy   import LinUCBPolicy
from .bandit_features import CTX_DIM
from .online_sim      import simulate_online_bandit
from .bandit_adapter import UCBPolicyAdapter
from .simulate        import (   # existing persona descriptions
    beg_imp, beg_notimp, int_imp, int_notimp, adv_imp, adv_notimp,
)

# -------- persona key → text ----------------------------------------------
PERSONA_POOL = {
    "beg_imp":       beg_imp,
    "beg_notimp":     beg_notimp,   
    "int_imp":       int_imp,
    "int_notimp":     int_notimp,
    "adv_imp":       adv_imp,
    "adv_notimp":     adv_notimp,
}

# -------- prompt-1 choices -------------------------------------------------
PROMPT1_POOL = [
    "Some schools offer distance learning as an option for students to attend "
    "classes from home by way of online or video conferencing. Do you think "
    "students would benefit from being able to attend classes from home? "
    "Take a position on this issue. Support your response with reasons and examples.",

    "Today the majority of humans own and operate cell phones on a daily basis. "
    "In essay form, explain if drivers should or should not be able to use cell "
    "phones in any capacity while operating a vehicle.",
]

# -------- CLI --------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser("Balanced LinUCB simulation (long format)")
    p.add_argument("--episodes", type=int, default=5,
                   help="Number of episodes *per persona* (default 5)")
    p.add_argument("--alpha", type=float, default=1.0,
                   help="LinUCB exploration parameter α (default 1.0)")
    p.add_argument("--policy", type=str, default="linucb",
                   choices=["linucb", "ucb1"],
                   help="Which policy to run: 'linucb' or 'ucb1' (default linucb).")
    p.add_argument("--outfile", type=Path, default=Path("data/linucb_online_ep50.csv"),
                   help="CSV output path")
    return p.parse_args()

def main() -> None:
    args = parse_args()

    # Choose the bandit object based on --policy
    if args.policy == "linucb":
        bandit = LinUCBPolicy(n_arms=4, dim=CTX_DIM, alpha=args.alpha)
    else:  # args.policy == "ucb1"
        # seed can be fixed or random; here we use 0 for reproducibility
        bandit = UCBPolicyAdapter(n_arms=4, seed=0)

    simulate_online_bandit(
        episodes_per_persona = args.episodes,
        bandit               = bandit,
        persona_pool         = PERSONA_POOL,
        prompt1_pool         = PROMPT1_POOL,
        csv_out              = args.outfile,
        verbose              = True,
    )

if __name__ == "__main__":
    main()


# run this for noncontextual
    # python -m src.cli_online \
    # --episodes 50 \
    # --policy ucb1 \
    # --outfile data/ucb1.csv

#     run this for contextual
    # python -m src.cli_online \
    # --episodes 50 \
    # --policy linucb \
    # --alpha 3 \
    # --outfile data/alpha3.csv