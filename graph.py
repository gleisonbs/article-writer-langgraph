from langgraph.graph import END, START, StateGraph

from nodes import (
    assemble_article,
    build_outline,
    draft_section,
    fan_out_sections,
    plan_research,
    web_search,
)
from schemas import State

builder = StateGraph(State)

builder.add_node("plan_research", plan_research)
builder.add_node("web_search", web_search)
builder.add_node("build_outline", build_outline)
builder.add_node("draft_section", draft_section)  # type: ignore
builder.add_node("assemble_article", assemble_article)

builder.add_edge(START, "plan_research")
builder.add_edge("plan_research", "web_search")
builder.add_edge("web_search", "build_outline")
builder.add_conditional_edges("build_outline", fan_out_sections, ["draft_section"])
builder.add_edge("draft_section", "assemble_article")
builder.add_edge("assemble_article", END)

graph = builder.compile()
