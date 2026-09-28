from collections.abc import Callable

from langgraph.types import Command

from graph import get_initial_state, graph
from logger import log_info, plural
from schemas import ArticleRequest


def run(state: dict | Command | None, config: dict) -> dict:
    for mode, chunk in graph.stream(state, config, stream_mode=["messages", "custom"]):  # type: ignore[call-overload]
        if mode == "messages":
            _print_draft_token(chunk)  # type: ignore[arg-type]
        elif mode == "custom":
            _log_custom(chunk)  # type: ignore[arg-type]

    snapshot = graph.get_state(config)  # type: ignore[arg-type]
    final_state = dict(snapshot.values)
    if snapshot.interrupts:
        final_state["__interrupt__"] = snapshot.interrupts
    return final_state


def _print_draft_token(message_chunk: tuple) -> None:
    token, meta = message_chunk
    if meta["langgraph_node"] == "draft_section":
        print(token.content, end="", flush=True)


def _log_custom(chunk: dict) -> None:
    if chunk.get("stage") == "coverage":
        facets = chunk["facets"]
        coverage = ", ".join(f"{facet}: {plural(n, 'domain')}" for facet, n in facets.items())
        log_info(f"Coverage so far — {coverage}")
    else:
        log_info(str(chunk))


def start_or_resume(request: ArticleRequest, topic: str, config: dict) -> dict:
    initial_state = get_initial_state(request)
    previous_state = graph.get_state(config).values  # type: ignore
    return run(None if previous_state else {"topic": topic, **initial_state}, config)


def resume_until_done(
    state: dict, config: dict, decide_edits: Callable[[dict], str | None]
) -> dict:
    while "__interrupt__" in state:                 # a resume can pause again
        outline_edits = decide_edits(state)
        state = run(Command(resume={"outline": outline_edits}), config)
    return state
