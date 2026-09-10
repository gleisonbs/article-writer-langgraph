from clients import model
from logger import log_info, plural
from schemas import SectionTask


def draft_section(task: SectionTask) -> dict:
    section = task["section"]

    log_info(f"Drafting: {section.heading}")

    others = [h for h in task["headings"] if h != section.heading]
    numbered = "\n\n".join(
        f"[{s['id']}] {s['title']}\n{s['content']}" for s in task["sources"]
    )
    cite = task["sources"][0]["id"] if task["sources"] else 1

    body = model.invoke(
        f"Write the section '{section.heading}' of an article.\n"
        f"Goal: {section.goal}\n"
        f"Other sections cover: {', '.join(others)} — do not duplicate them.\n"
        f"Use ONLY the sources below and cite them inline like [{cite}].\n\n"
        f"{numbered}"
    ).content

    log_info(f"Finished “{section.heading}” ({plural(len(str(body)), 'character')})")

    return {"drafted": [section.model_copy(update={"draft": body})]}
