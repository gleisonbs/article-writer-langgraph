from collections.abc import Callable

from langgraph.types import Command

from graph import get_initial_state, graph
from logger import log_info, plural
from schemas import ArticleRequest


def run(state, config) -> dict:
    """Stream a run to completion; nodes log their own progress as they go."""
    for mode, chunk in graph.stream(
        state, config, stream_mode=["updates", "messages", "custom"]
    ):
        if mode == "custom":
            _log_custom(chunk) # type: ignore
        elif mode == "messages":
            token, meta = chunk
            if meta["langgraph_node"] == "draft_section":  # type: ignore
                print(token.content, end="", flush=True)  # type: ignore

    snapshot = graph.get_state(config)
    return {
        **snapshot.values,  # resurface the pause, if the run just interrupted
        **({"__interrupt__": snapshot.interrupts} if snapshot.interrupts else {}),
    }


def _log_custom(chunk: dict) -> None:
    if chunk.get("stage") == "coverage":
        facets = chunk["facets"]
        coverage = ", ".join(f"{facet}: {plural(n, 'domain')}" for facet, n in facets.items())
        log_info(f"Coverage so far — {coverage}")
    else:
        log_info(str(chunk))


def start_or_resume(request: ArticleRequest, topic: str, config: dict) -> dict:
    """None continues this thread; the initial state is only for an empty one."""
    initial_state = get_initial_state(request)
    previous_state = graph.get_state(config).values  # type: ignore
    return run(None if previous_state else {"topic": topic, **initial_state}, config)


def resume_until_done(
    state: dict, config: dict, decide_edits: Callable[[dict], str | None]
) -> dict:
    """Resume an interrupted run until it completes.

    `decide_edits` is asked, on each pause, for the outline edits to resume with —
    or None to keep the outline as proposed.
    """
    while "__interrupt__" in state:                 # a resume can pause again
        outline_edits = decide_edits(state)
        state = run(Command(resume={"outline": outline_edits}), config)
    return state
