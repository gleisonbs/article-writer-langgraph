from clients import model
from logger import log_header, log_info, log_list, plural
from nodes.render_brief import render_brief
from nodes.research_is_sufficient import facets_below_min_domain_count
from schemas import ResearchPlan, State


def plan_research(state: State) -> dict:
    log_header("Planning Research")

    log_info(f"Topic: {state['topic']}")
    log_info(f"Audience: {state['audience']}")
    log_info("Asking the model for search queries")

    facets_with_gaps = facets_below_min_domain_count(state) if state["sources"] else []

    plan = model.with_structured_output(ResearchPlan).invoke(
        render_brief(state["topic"], state["audience"], facets_with_gaps, state["query_log"])
    )

    new_facets = [f for f in plan.facets if f not in state["facets"]]  # type: ignore
    if new_facets:
        log_info(f"Identified {plural(len(new_facets), 'new facet')}:")
        log_list(new_facets)

    log_info(f"Planned {plural(len(plan.queries), 'query', 'queries')}:")  # type: ignore
    log_list([f"{q.query}  [{q.facet}]" for q in plan.queries])  # type: ignore

    return {
        "facets": new_facets,
        "queries": plan.queries,  # type: ignore
        "research_passes": state["research_passes"] + 1,
    }
