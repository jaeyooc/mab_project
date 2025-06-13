#feedback.py
from enum import Enum
from typing import Dict, Callable

from src.utils import ask_gpt

class FeedbackArm(str, Enum):
    """Four feedback styles used in the simulation."""

    SOC_LOW = "socratic_low"   # questions, sentence‑level
    SOC_HIGH = "socratic_high"  # questions, organization‑level
    DIR_LOW = "direct_low"      # commands, sentence‑level
    DIR_HIGH = "direct_high"     # commands, organization‑level


SYSTEM_PROMPT = (
    "You are an academic writing tutor. "
    "Follow the user's instruction exactly."
)

# ---- user‑prompt templates keyed by feedback arm ---------------------------
_USER_TEMPLATE: Dict[FeedbackArm, str] = {
    FeedbackArm.SOC_LOW: (
        "You are an academic writing tutor for {grade_level} students writing "
        "on the following essay prompt: {writing_prompt}. You will provide 2 socratic feedback (feedback entirely in the form of guiding questions) and focus strictly on sentence‑level clarity, word choice, and grammar. "
        "Do not comment on structure, argument, or organization, and do not give any direct commands or suggestions."
    ),
    FeedbackArm.SOC_HIGH: (
        "You are an academic writing tutor for {grade_level} students writing "
        "on the following essay prompt: {writing_prompt}. You will provide 2 socratic feedback (feedback entirely in the form of guiding questions) and focus strictly on high‑level organization, logical flow, and how ideas are sequenced. "
        "Do not comment on grammar, word choice, or any sentence‑level issues, and do not give any direct commands or suggestions."
    ),
    FeedbackArm.DIR_LOW: (
        "You are an academic writing tutor for {grade_level} students writing "
        "on the following essay prompt: {writing_prompt}. You will provide 2 direct commands and suggestions and focus strictly on sentence‑level clarity, word choice, and grammar. "
        "Do not comment on structure, argument, or organization. Do not ask students guiding questions—just give the commands."
    ),
    FeedbackArm.DIR_HIGH: (
        "You are an academic writing tutor for {grade_level} students writing "
        "on the following essay prompt: {writing_prompt}. You will provide 2 direct commands and suggestions and focus strictly on high‑level organization, logical flow, and how ideas are sequenced. "
        "Do not comment on grammar, word choice, or any sentence‑level issues. Do not ask students guiding questions—just give the commands."
    ),
}


def generate_feedback(
    *,
    essay: str,
    arm: FeedbackArm,
    grade_level: str,
    writing_prompt: str,
    ask_fn: Callable = ask_gpt,
    model: str = "gpt-4o",
    temperature: float = 0.5,
) -> str:
    """Generate feedback in the requested *arm* style.

    Returns
    -------
    str
        The feedback text (no metadata).
    """
    user_prompt = _USER_TEMPLATE[arm].format(
        grade_level=grade_level,
        writing_prompt=writing_prompt,
        essay=essay,
    )

    return ask_fn(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        model=model,
        temperature=temperature,
    )
