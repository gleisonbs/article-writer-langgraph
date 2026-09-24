from clients import model
from logger import log_info, log_list, plural
from schemas import SectionTask

CITATION_RULE = (
    'Cite as you go: after each claim taken from a source, add [id: "phrase"], '
    "where id is the source's number and phrase is copied word for word from that "
    "source. Only cite the sources listed below."
)


def other_headings(task: SectionTask) -> str:
    return ", ".join(h for h in task["headings"] if h != task["section"].heading)


def render_sources(task: SectionTask) -> str:
    return "\n\n".join(
        f"[{s['id']}] {s['title']}\n{s['content']}" for s in task["sources"]
    )


def draft_prompt(task: SectionTask) -> str:
    section = task["section"]
    return (
        f'Write the section "{section.heading}" of an article for '
        f"{task['audience']}, in a {task['tone']} register.\n\n"
        f"Goal: {section.goal}\n"
        f"Length: about {section.target_words} words.\n"
        f"Other sections cover: {other_headings(task)}. Do not repeat them.\n\n"
        f"{CITATION_RULE}\n\n"
        "Return only the section's prose, without its heading.\n\n"
        f"<sources>\n{render_sources(task)}\n</sources>"
    )


def redraft_prompt(task: SectionTask, problems: list[str]) -> str:
    section = task["section"]
    listed = "\n".join(f"- {p}" for p in problems)
    return (
        f'Revise this draft of the section "{section.heading}", from an article '
        f"for {task['audience']} in a {task['tone']} register.\n\n"
        f"A reviewer found these problems:\n{listed}\n\n"
        "Fix every one, and change as little else as you can: keep the claims, "
        "order and citations that weren't flagged.\n"
        "- A quote that isn't in its source, or only loosely matches it: replace "
        "it with a phrase copied word for word from that source, or drop the claim.\n"
        "- A citation to a source that doesn't exist: cite a listed source "
        "instead, or drop the claim.\n"
        "- A tone lapse: rewrite that passage in the target register.\n\n"
        f"Stay near {section.target_words} words, this section's share of the "
        f"article, and leave what the other sections cover to them: "
        f"{other_headings(task)}.\n\n"
        f"{CITATION_RULE}\n\n"
        "Return only the revised prose, without its heading.\n\n"
        f"<draft>\n{section.draft}\n</draft>\n\n"
        f"<sources>\n{render_sources(task)}\n</sources>"
    )


def draft_section(task: SectionTask) -> dict:
    section = task["section"]
    problems = task.get("problems") or []

    if problems:
        log_info(f"Redrafting: {section.heading} — {plural(len(problems), 'problem')} to fix:")
        log_list(problems)
        prompt = redraft_prompt(task, problems)
    else:
        log_info(f"Drafting: {section.heading} - {section.target_words} words")
        prompt = draft_prompt(task)

    body = model.invoke(prompt).content

    log_info(f"Finished “{section.heading}” ({plural(len(str(body)), 'character')})")

    return {"drafted": [section.model_copy(update={"draft": body})]}
