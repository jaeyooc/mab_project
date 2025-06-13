# simulation
from src.batch import batch_sim_three_two_revisions as run_sim
from src.feedback import FeedbackArm

# ---------------------------------------------------------------------------
#  PERSONA DEFINITIONS 
# ---------------------------------------------------------------------------

beg_imp = (
    "A 10th‑grade student writing at CEFR A1‑A2 level. Uses basic vocabulary and simple sentence structures, "
    "often with grammar mistakes. Actively tries to improve with each draft based on feedback."
)

beg_notimp = (
    "A 10th‑grade student writing at CEFR A1‑A2 level. Uses basic vocabulary and simple sentence structures, "
    "often with grammar mistakes. Attempts to revise but shows little meaningful improvement across drafts."
)

int_imp = (
    "A 10th‑grade student writing at CEFR B1–B2 level. Uses complete sentences, connects ideas logically, "
    "and uses moderate vocabulary. Actively tries to improve with each draft based on feedback."
)

int_notimp = (
    "A 10th‑grade student writing at CEFR B1–B2 level. Uses complete sentences, connects ideas logically, "
    "and uses moderate vocabulary. Attempts to revise but shows little meaningful improvement across drafts."
)

adv_imp = (
    "A 10th‑grade student at CEFR C1–C2 level. Writes fluently and with control of tone, structure, and argument. "
    "Actively tries to improve with each draft based on feedback."
)

adv_notimp = (
    "A 10th‑grade student at CEFR C1–C2 level. Writes fluently and with control of tone, structure, and argument. "
    "Attempts to revise but shows little meaningful improvement across drafts."
)

PERSONAS = [beg_imp, beg_notimp, int_imp, int_notimp, adv_imp, adv_notimp]  

# ---------------------------------------------------------------------------
#  ESSAY PROMPTS  (edit freely)
# ---------------------------------------------------------------------------

prompt_dist = (
    "Some schools offer distance learning as an option for students to attend classes from home by way of online "
    "or video conferencing. Do you think students would benefit from being able to attend classes from home? "
    "Take a position on this issue. Support your response with reasons and examples."
)

prompt_summer = (
    "Some schools require students to complete summer projects to assure they continue learning during their break. "
    "Should these summer projects be teacher‑designed or student‑designed? Take a position on this question. "
    "Support your response with reasons and specific examples."
)

prompt_phone = "Today the majority of humans own and operate cell phones on a daily basis. In essay form, explain if drivers should or should not be able to use cell phones in any capacity while operating a vehicle."

prompt_multiple = "When people ask for advice, they sometimes talk to more than one person. Explain why seeking multiple opinions can help someone make a better choice. Use specific details and examples in your response."

PROMPTS = [prompt_dist, prompt_summer]

# ---------------------------------------------------------------------------
#  MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    csv_path = run_sim(
        runs=50,
        personas=PERSONAS,
        grade_level="10th-grade",
        prompts=PROMPTS,
        arms=[FeedbackArm.SOC_HIGH,FeedbackArm.SOC_LOW, FeedbackArm.DIR_HIGH, FeedbackArm.DIR_LOW],
        verbose=True,
        csv_out = "0527_sim_batch_50rep.csv"
    )
    print(f"Simulation complete. Check {csv_path} for results.")