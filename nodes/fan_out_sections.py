from langgraph.types import Send

from logger import log_header, log_info, plural
from schemas import State


def fan_out_sections(state: State):
    log_header("Dispatching Sections")

    by_id = {s["id"]: s for s in state["sources"]}
    headings = [s.heading for s in state["outline"]]

    log_info(f"Sending {plural(len(state['outline']), 'section')} off to be drafted:")

    sends: list[Send] = []
    for section in state["outline"]:
        sources = [by_id[id] for id in section.source_ids if id in by_id]
        missing = [id for id in section.source_ids if id not in by_id]
        log_info(
            f"  {section.index}. {section.heading} — {plural(len(sources), 'source')}"
        )
        if missing:
            unknown = ", ".join(str(id) for id in missing)
            log_info(f"     Skipping unknown source ids: {unknown}")
        sends.append(
            Send(
                "draft_section",
                {
                    "section": section,
                    "headings": headings,
                    "sources": sources,
                },
            )
        )

    return sends
