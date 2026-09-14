from clients import model
from logger import log_header, log_info, plural
from schemas import Outline, State


def build_outline(state: State) -> dict:
    log_header("Building the Outline")

    log_info(f"Cataloging {plural(len(state['sources']), 'source')}")

    catalog = "\n".join(
        f"[{s['id']} {s['title']}: {s['content'][:200]}]" for s in state["sources"]
    )

    log_info("Asking the model for an outline")

    outline = model.with_structured_output(Outline).invoke(
        f"Plan an article about: {state['topic']}\n\n"
        f"Break it into 3-6 sections. For each: a heading, what it should "
        f"accomplish, and which sources it needs (by id).\n\n"
        f"Sources:\n{catalog}"
    )

    log_info(f"Outlined {plural(len(outline.sections), 'section')}:")  # type: ignore
    for section in outline.sections:  # type: ignore
        cites = ", ".join(str(id) for id in section.source_ids)
        log_info(f"  {section.index}. {section.heading} (sources {cites})")

    section_target_words = state["target_words"] // len(outline.sections)  # type: ignore
    for section in outline.sections:  # type: ignore
        section.target_words = section_target_words
    return {"outline": outline.sections}  # type: ignore
