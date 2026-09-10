from logger import log_header, log_info, plural
from schemas import State


def assemble_article(state: State) -> dict:
    log_header("Assembling the Article")

    log_info(f"Putting {plural(len(state['drafted']), 'section')} in order:")

    ordered = sorted(state["drafted"], key=lambda s: s.index)
    for section in ordered:
        log_info(f"  {section.index}. {section.heading}")

    article = "\n\n".join(f"## {s.heading}\n\n{s.draft}" for s in ordered)

    log_info(f"Article is ready ({plural(len(article), 'character')})")

    return {"article": article}
