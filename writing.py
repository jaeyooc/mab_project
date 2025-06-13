# writing.py
# WRITE/REWRITE HELPERS

from pathlib import Path
from typing import Callable, Dict, List, Optional
from src.utils import ask_gpt

def rewrite_essay(
    *,
    essay: str,
    feedback: str,
    persona: str,
    ask_fn: Callable = ask_gpt,
    model: str = "gpt-4o",
    temperature: float = 1.0,
) -> str:
    """Return a revision of *essay* that addresses *feedback* in *persona* voice."""

    system_prompt = (
        f"You are revising your own essay in the role of a {persona}.\n"
        f"Your goal is to address the feedback, given that you have writing ability of a {persona}."
    )

    user_prompt = (
        f"You are a {persona}. Make only the changes needed to satisfy the feedback. "
        f"Only address the feedback and do not add new claims or omit major content.\n\n"
        "----- ORIGINAL ESSAY -----\n"
        f"{essay}\n\n"
        "----- FEEDBACK TO INCORPORATE -----\n"
        f"{feedback}\n\n"
        "Begin your revised essay below:\n"
    )

    return ask_fn(
        system=system_prompt,
        user=user_prompt,
        model=model,
        temperature=temperature,
    )


def write_essay(
    *,
    persona: str,
    essay_prompt: str,
    use_history: bool = False,
    history: Optional[List[Dict[str, str]]] = None,
    ask_fn: Callable = ask_gpt,
    model: str = "gpt-4o",
    temperature: float = 0.5,
    max_history: int = 4,
) -> str:
    """Generate a fresh essay (optionally with history for learning)."""

    system_prompt = (
        f"You are writing as **{persona}**.\n"
        "Maintain that persona's typical vocabulary, tone, and error profile.\n"
        "Respond ONLY with the full essay—no meta comments."
    )

    parts: List[str] = [
        f"NEW ASSIGNMENT PROMPT:\n{essay_prompt}\n",
        "Write an essay that addresses the prompt above. Try to write in 500 to 1000 words.",
    ]

    if use_history and history:
        history_to_use = history[-max_history:]
        parts.append(
            "\nBelow are your PREVIOUS essays and the feedback you received. "
            "Demonstrate learning from the feedback, show gradual improvement, "
            f"but do NOT suddenly become perfect. Note that you are {persona}."
        )
        for i, item in enumerate(history_to_use, 1):
            parts.extend([
                f"\n--- Prior Example {i} ---",
                f"Prompt  : {item['prompt']}",
                "",
                "Essay   :",
                item["essay"],
                "",
                "Feedback:",
                item["feedback"],
                f"--- End Example {i} ---",
            ])

    parts.append("\nBegin your new essay below:\n")
    user_prompt = "\n".join(parts)

    return ask_fn(
        system=system_prompt,
        user=user_prompt,
        model=model,
        temperature=temperature,
    )
