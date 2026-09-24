import json

from langgraph.types import interrupt

from nodes.research_is_sufficient import domains_per_facet
from schemas import Section, State


def human_review(state: State) -> dict:
    decision = interrupt(
        {
            "outline": [s.model_dump() for s in state["outline"]],
            "sources": [
                {"id": s["id"], "title": s["title"], "url": s["url"]}
                for s in state["sources"]
            ],
            "coverage": domains_per_facet(state),
        }
    )

    edited = decision.get("outline")
    if not edited:
        return {"outline": state["outline"]}
    return {"outline": [Section(**{**s, "index": i}) for i, s in enumerate(json.loads(edited), 1)]}