# batch
import csv
import time
from pathlib import Path
from typing import Callable, Dict, List

from src.feedback import FeedbackArm, generate_feedback
from src.grading import RUBRIC, score_essay
from src.writing import write_essay, rewrite_essay
from src.utils import ask_gpt

# ---------------------------------------------------------------------------
#  quick grading wrapper
# ---------------------------------------------------------------------------

def _grade(*, essay: str, ask_fn: Callable, rubric: str, model: str, temperature: float) -> int:
    score, _ = score_essay(
        essay=essay,
        rubric=rubric,
        ask_fn=ask_fn,
        model=model,
        temperature=temperature,
    )
    return score


# ---------------------------------------------------------------------------
#  Batch simulation: two prompts, two revisions on prompt1
# ---------------------------------------------------------------------------

def batch_sim_three_two_revisions(
    *,
    runs: int,
    personas: List[str],
    grade_level: str,
    prompts: List[str],  # [prompt1, prompt2]
    arms: List[FeedbackArm],
    gpt_model: str = "gpt-4o",
    temperature_writing: float = 1.0,
    temperature_score: float = 0.5,
    temperature_feedback: float = 0.5,
    ask_fn: Callable = ask_gpt,
    rubric: str = RUBRIC,
    csv_out: str,
    verbose: bool = True,
) -> Path:
    """Run *runs* simulations for every (persona, arm) pair and write CSV."""

    if len(prompts) != 2:
        raise ValueError("`prompts` must contain exactly two strings.")
    if not personas:
        raise ValueError("`personas` list must contain at least one persona.")
    if not arms:
        raise ValueError("`arms` list must contain at least one FeedbackArm.")

    rows: List[Dict] = []

    for persona in personas:
        for arm in arms:
            if verbose:
                print(f"\n>>> Persona: {persona} | Arm: {arm.value}\n" + "-" * (22 + len(persona) + len(arm.value)))

            for run_idx in range(1, runs + 1):
                tag = f"[{persona} | {arm.value}] Run {run_idx}/{runs}"

                # -------- Draft 1 ----------------------------------------
                if verbose:
                    print(f"{tag}: drafting essay 1 …")
                draft1 = write_essay(
                    persona=persona,
                    essay_prompt=prompts[0],
                    use_history=False,
                    history=[],
                    ask_fn=ask_fn,
                    model=gpt_model,
                    temperature=temperature_writing,
                )
                score1 = _grade(
                    essay=draft1,
                    ask_fn=ask_fn,
                    rubric=rubric,
                    model=gpt_model,
                    temperature=temperature_score,
                )

                # -------- Feedback 1 → Draft 2 --------------------------
                if verbose:
                    print(f"{tag}: feedback 1 …")
                fb1 = generate_feedback(
                    essay=draft1,
                    arm=arm,
                    grade_level=grade_level,
                    writing_prompt=prompts[0],
                    ask_fn=ask_fn,
                    model=gpt_model,
                    temperature=temperature_feedback,
                )
                if verbose:
                    print(f"{tag}: rewriting → draft 2 …")
                draft2 = rewrite_essay(
                    essay=draft1,
                    feedback=fb1,
                    persona=persona,
                    ask_fn=ask_fn,
                    model=gpt_model,
                    temperature=temperature_writing,
                )
                score2 = _grade(
                    essay=draft2,
                    ask_fn=ask_fn,
                    rubric=rubric,
                    model=gpt_model,
                    temperature=temperature_score,
                )

                # -------- Feedback 2 → Draft 3 --------------------------
                if verbose:
                    print(f"{tag}: feedback 2 …")
                fb2 = generate_feedback(
                    essay=draft2,
                    arm=arm,
                    grade_level=grade_level,
                    writing_prompt=prompts[0],
                    ask_fn=ask_fn,
                    model=gpt_model,
                    temperature=temperature_feedback,
                )
                if verbose:
                    print(f"{tag}: rewriting → draft 3 …")
                draft3 = rewrite_essay(
                    essay=draft2,
                    feedback=fb2,
                    persona=persona,
                    ask_fn=ask_fn,
                    model=gpt_model,
                    temperature=temperature_writing,
                )
                score3 = _grade(
                    essay=draft3,
                    ask_fn=ask_fn,
                    rubric=rubric,
                    model=gpt_model,
                    temperature=temperature_score,
                )

                # -------- Draft 4 (prompt 2, history‑aware) -------------
                history = [{"prompt": prompts[0], "essay": draft3, "feedback": fb2}]
                if verbose:
                    print(f"{tag}: drafting essay 2 (with history) …")
                draft4 = write_essay(
                    persona=persona,
                    essay_prompt=prompts[1],
                    use_history=True,
                    history=history,
                    ask_fn=ask_fn,
                    model=gpt_model,
                    temperature=temperature_writing,
                )
                score4 = _grade(
                    essay=draft4,
                    ask_fn=ask_fn,
                    rubric=rubric,
                    model=gpt_model,
                    temperature=temperature_score,
                )

                # -------- Log row --------------------------------------
                rows.append(
                    {
                        "run": run_idx,
                        "persona": persona,
                        "arm": arm.value,
                        "grade_level": grade_level,
                        "gpt_model": gpt_model,
                        "temperature_writing": temperature_writing,
                        "temperature_feedback": temperature_feedback,
                        "temperature_score": temperature_score,
                        "prompt_1": prompts[0],
                        "prompt_1_draft_1": draft1,
                        "prompt_1_draft_1_score": score1,
                        "prompt_1_draft_1_feedback": fb1,
                        "prompt_1_revised_draft_2": draft2,
                        "prompt_1_revised_draft_2_score": score2,
                        "prompt_1_revised_draft_2_feedback": fb2,
                        "prompt_1_revised_draft_3": draft3,
                        "prompt_1_revised_draft_3_score": score3,
                        "prompt_2": prompts[1],
                        "prompt_2_draft_1": draft4,
                        "prompt_2_draft_1_score": score4,
                    }
                )
                time.sleep(0.2)

    # -------- Write CSV ------------------------------------------------------
    if not rows:
        raise RuntimeError("No rows were generated—check your inputs.")

    header = list(rows[0])
    csv_out = Path(csv_out)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

    if verbose:
        print(
            f"\nSaved {len(rows)} rows (across {len(personas)} persona(s) × {len(arms)} arm(s)) to {csv_out.resolve()}"
        )
    return csv_out
