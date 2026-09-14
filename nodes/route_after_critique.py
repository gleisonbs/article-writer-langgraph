from langgraph.types import Send

from logger import log_header, log_info, plural
from schemas import State

BUDGET = 3


def route_after_critique(state: State):
    log_header("Routing After Critique")

    blockers = [f for f in state["findings"] if f.severity == "blocker"]
    scores = state["scores"]
    improving = len(scores) < 2 or scores[-1]["failures"] < scores[-2]["failures"]

    if not (blockers and state["revision_count"] < BUDGET and improving):
        reason = (
            "no blockers remain"
            if not blockers
            else f"the revision budget of {BUDGET} is used up"
            if state["revision_count"] >= BUDGET
            else "the last revision did not improve on the one before it"
        )
        log_info(f"Sending the article to final polish — {reason}")
        return "final_polish"

    flagged = sorted({f.section_index for f in blockers if f.section_index is not None})

    by_id = {s["id"]: s for s in state["sources"]}
    by_index = {s.index: s for s in state["drafted"]}

    log_info(
        f"Sending {plural(len(flagged), 'section')} back for revision "
        f"(pass {state['revision_count'] + 1}/{BUDGET}):"
    )
    for i in flagged:
        problems = len([f for f in blockers if f.section_index in (i, None)])
        log_info(f"  {i}. {by_index[i].heading} — {plural(problems, 'blocker')}")

    return [
        Send(
            "draft_section",
            {
                "section": by_index[i],
                "headings": [s.heading for s in state["outline"]],
                "sources": [by_id[j] for j in by_index[i].source_ids if j in by_id],
                "audience": state["audience"],
                "tone": state["tone"],
                "problems": [
                    f.detail for f in state["findings"] if f.section_index in (i, None)
                ],
            },
        )
        for i in flagged
    ]
