from clients import model
from logger import log_header, log_info, plural
from nodes.render_brief import render_brief
from nodes.research_is_sufficient import gaps_in
from schemas import ResearchPlan, State


def plan_research(state: State) -> dict:
    log_header("Planning Research")

    log_info(f"Topic: {state['topic']}")
    log_info(f"Audience: {state['audience']}")
    log_info("Asking the model for search queries")

    gaps = gaps_in(state) if state["sources"] else []

    plan = model.with_structured_output(ResearchPlan).invoke(
        render_brief(state["topic"], state["audience"], gaps, state["query_log"])
    )

    new_facets = [f for f in plan.facets if f not in state["facets"]]  # type: ignore
    if new_facets:
        log_info(f"Identified {plural(len(new_facets), 'new facet')}:")
        for facet in new_facets:
            log_info(f"  • {facet}")

    log_info(f"Planned {plural(len(plan.queries), 'query', 'queries')}:")  # type: ignore
    for query in plan.queries:  # type: ignore
        log_info(f"  • {query.query}  [{query.facet}]")

    return {
        "facets": new_facets,
        "queries": plan.queries,  # type: ignore
        "research_passes": state["research_passes"] + 1,
    }
