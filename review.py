from logger import log_info, log_paste, log_prompt, log_warning
from runner import resume_until_done
from utils import display_formatted_outline, show_proposal


def confirm(prompt: str) -> bool:
    return log_prompt(prompt).strip().lower() == "y"


def request_outline_edits(state: dict, thread: str | None) -> str:
    log_info("Edit the outline below and paste it back as JSON:")
    display_formatted_outline(state)
    if not confirm("\nInput edits? [y/N] "):
        log_warning(f"Left paused. Resume later with the same thread id: {thread}")
        raise SystemExit(0)
    return log_paste("Outline edits")


def review_outline(state: dict, thread: str | None) -> str | None:
    show_proposal(state["__interrupt__"][0].value)
    if confirm("\napprove? [y/N] "):
        return None
    return request_outline_edits(state, thread)


def run_until_done(state: dict, thread: str | None, config: dict) -> dict:
    return resume_until_done(state, config, lambda s: review_outline(s, thread))
