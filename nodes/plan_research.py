from clients import model
from logger import log_header, log_info, plural
from schemas import SearchQueries, State


def plan_research(state: State) -> dict:
    log_header("Planning Research")

    log_info(f"Topic: {state['topic']}")
    log_info("Asking the model for search queries")

    plan = model.with_structured_output(SearchQueries).invoke(
        f"Write 3-6 web search queries to research an article  about: {state['topic']}"
    )

    log_info(f"Planned {plural(len(plan.queries), 'query', 'queries')}:")  # type: ignore
    for query in plan.queries:  # type: ignore
        log_info(f"  • {query}")

    return {"queries": plan.queries}  # type: ignore
