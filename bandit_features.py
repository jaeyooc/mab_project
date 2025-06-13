#bandit.py
from __future__ import annotations
import numpy as np
import textstat
from typing import Dict


persona2vec = {
    # [beginner?, intermediate? , advanced? improve or not?]
    "beg_imp": [1,0,0,1],
    "beg_notimp": [1,0,0,0],
    "int_imp": [0,1,0,1],
    "int_notimp": [0,1,0,0],
    "adv_imp":      [0, 0, 1, 1],
    "adv_notimp":    [0, 0, 1, 0],


}

PERSONA_DIM = 4
LIVE_DIM = 3
CTX_DIM = PERSONA_DIM + LIVE_DIM

def build_x(essay:str, persona_key: str, base_score:float) -> np.ndarray:
    """""Return a numeric context vector """""""""
    persona_vec = np.array(persona2vec[persona_key], dtype = float)
    live_vec = np.array([
        len(essay.split()), #token count
        textstat.flesch_reading_ease(essay), #flesch reading score for readability
        base_score # holistic score before any feedback (first draft score)
    ], dtype = float)
    return np.concatenate([persona_vec, live_vec])


