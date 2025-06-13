"""
online_sim.py  –  LONG-format episode simulator
------------------------------------------------
• 3 feedback rounds (bandit chooses an arm each round)
• 1 transfer step credited to the last arm
• Δ-score reward
• Adds `episode_id` so you can group rows by student
"""

from __future__ import annotations
import csv, time, random
from pathlib import Path
from typing import Dict, List

from .utils           import ask_gpt
from .writing         import write_essay, rewrite_essay
from .feedback        import FeedbackArm, generate_feedback
from .grading         import score_essay
from .linucb_policy   import LinUCBPolicy
from .bandit_features import build_x, CTX_DIM
import textstat

# ---------------------------------------------------------------------------
#  fixed feedback arms
# ---------------------------------------------------------------------------
ARMS: List[FeedbackArm] = [
    FeedbackArm.SOC_LOW,
    FeedbackArm.SOC_HIGH,
    FeedbackArm.DIR_LOW,
    FeedbackArm.DIR_HIGH,
]

def lexical_score(text: str) -> float:
    """
    Very simple lex-complexity proxy:
        unique_word_ratio  =  (# unique words) / (total words)
    You can swap this for textstat.lexical_density or any other metric.
    """
    words = [w.lower() for w in text.split()]
    if not words:
        return 0.0
    return len(set(words)) / len(words)


# ---------------------------------------------------------------------------
#  prompt-pairing helper
# ---------------------------------------------------------------------------
def paired_prompt(prompt1: str) -> str:
    if "distance learning" in prompt1.lower():
        return (
            "Some schools require students to complete summer projects to assure they "
            "continue learning during their break. Should these summer projects be "
            "teacher-designed or student-designed? Take a position on this question. "
            "Support your response with reasons and specific examples."
        )
    return (
        "When people ask for advice, they sometimes talk to more than one person. "
        "Explain why seeking multiple opinions can help someone make a better choice. "
        "Use specific details and examples in your response."
    )

# ---------------------------------------------------------------------------
#  one episode  →  returns *four* log rows
# ---------------------------------------------------------------------------
def run_episode(
    *,
    bandit: LinUCBPolicy,
    persona_key: str,
    persona_text: str,
    prompt1: str,
    grade_level: str = "10th-grade",
    model: str = "gpt-4o",
    t_write: float = 1.0,
    t_fb: float = 0.5,
    t_score: float = 0.0,
) -> List[dict]:
    rows: List[dict] = []

    # ---- Draft-1 ----------------------------------------------------------
    draft = write_essay(persona = persona_text, essay_prompt = prompt1, use_history = False,
                        ask_fn=ask_gpt, model=model, temperature=t_write)
    score = score_essay(draft, model=model, temperature=t_score)[0]

    last_ctx = None
    last_arm_idx = None

    # ---- three feedback rounds -------------------------------------------
    for r in (1, 2, 3):
        ctx     = build_x(draft, persona_key, score)
        arm_idx = bandit.select_arm(ctx)
        arm     = ARMS[arm_idx]

        fb = generate_feedback(essay = draft, arm = arm, grade_level = grade_level, writing_prompt = prompt1,
                               ask_fn=ask_gpt, model=model, temperature=t_fb)
        new_draft = rewrite_essay(essay = draft, feedback = fb, persona = persona_text,
                                  ask_fn=ask_gpt, model=model, temperature=t_write)
        new_score = score_essay(new_draft, model=model, temperature=t_score)[0]
        reward    = new_score - score

        bandit.update(arm_idx, reward, ctx)

        rows.append({
            "round":        r,               # 1,2,3
            "persona_key":  persona_key,
            "prompt":       prompt1,
            "essay_text":   draft,           # essay BEFORE this feedback
            "lex_score":    lexical_score(draft),
            "arm":          arm.value,
            "feedback_text": fb,             
            "score_before": score,
            "score_after":  new_score,
            "reward":       reward,
        })

        draft, score = new_draft, new_score
        last_ctx, last_arm_idx = ctx, arm_idx

    # ---- transfer step ----------------------------------------------------
    prompt2 = paired_prompt(prompt1)
    t_draft = write_essay(
        persona = persona_text, essay_prompt= prompt2, use_history= True,
        history=[{"prompt": prompt1, "essay": draft, "feedback": fb}],
        ask_fn=ask_gpt, model=model, temperature=t_write,
    )
    t_score  = score_essay(t_draft, model=model, temperature=t_score)[0]
    t_reward = t_score - rows[0]["score_before"]

    bandit.update(last_arm_idx, t_reward, last_ctx)

    rows.append({
    "round":        "transfer",
    "persona_key":  persona_key,
    "prompt":       prompt2,
    "essay_text":   draft,           # last revision of prompt-1
    "lex_score":    lexical_score(draft),
    "arm":          ARMS[last_arm_idx].value,
    "feedback_text": "",             # no new feedback in transfer step
    "score_before": score,
    "score_after":  t_score,
    "reward":       t_reward,
})
    return rows

# ---------------------------------------------------------------------------
#  run many episodes – balanced per persona – LONG format (shuffled)
# ---------------------------------------------------------------------------
def simulate_online_bandit(
    *,
    episodes_per_persona: int,
    bandit: LinUCBPolicy,
    persona_pool: Dict[str, str],
    prompt1_pool: List[str],
    csv_out: Path,
    verbose: bool = True,
) -> Path:

    # Make sure the output folder exists
    csv_out.parent.mkdir(parents=True, exist_ok=True)

    # Total number of episodes = #personas × episodes_per_persona
    total_students = episodes_per_persona * len(persona_pool)  # e.g. 6 × 50 = 300

    # 1) Build a flat list “playlist” of length==total_students.
    #    Each element is a tuple (persona_key, persona_text).
    #    This list contains exactly `episodes_per_persona` copies of each persona.
    choices: list[tuple[str, str]] = []
    for persona_key, persona_text in persona_pool.items():
        for _ in range(episodes_per_persona):
            choices.append((persona_key, persona_text))

    # 2) Shuffle that list so episodes are randomly interleaved across all personas.
    #    Using a fixed seed here ensures reproducibility—remove `random_seed` if you don’t need that.
    random_seed = 42
    rnd = random.Random(random_seed)
    rnd.shuffle(choices)
    # Now `choices` is something like:
    #   [("int_imp", "..."), ("beg_notimp", "..."), ("adv_imp", "..."), ("beg_imp", "..."), …]
    # exactly 300 entries, in random order.

    epi = 0
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = None

        # 3) Iterate over the shuffled episodes—no nested loops here!
        for (persona_key, persona_text) in choices:
            epi += 1

            # Pick one random prompt1 as before
            prompt1 = random.choice(prompt1_pool)

            # Run a single “episode” (4 rows: rounds 1–3 + transfer)
            rows = run_episode(
                bandit       = bandit,
                persona_key  = persona_key,
                persona_text = persona_text,
                prompt1      = prompt1,
            )

            # Tag each of those 4 rows with the same global student ID = epi
            for r in rows:
                r["episode_id"] = epi

            # Initialize CSV writer once (on the first episode)
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()

            # Write all 4 rows for this student-episode, then flush
            writer.writerows(rows)
            f.flush()

            if verbose:
                print(f"Episode {epi}/{total_students} | persona = {persona_key}")
            time.sleep(0.05)

    if verbose:
        print(f"\nSaved log to {csv_out.resolve()}")
    return csv_out