from langgraph.graph import END, START, StateGraph

from nodes import (
    assemble_article,
    build_outline,
    critique,
    draft_section,
    fan_out_sections,
    final_polish,
    plan_research,
    reseach_is_sufficient,
    route_after_critique,
    web_search,
)
from schemas import State

builder = StateGraph(State)

builder.add_node("plan_research", plan_research)
builder.add_node("web_search", web_search)
builder.add_node("build_outline", build_outline)
builder.add_node("draft_section", draft_section)  # type: ignore
builder.add_node("assemble_article", assemble_article)
builder.add_node("critique", critique)
builder.add_node("final_polish", final_polish)

builder.add_edge(START, "plan_research")
builder.add_edge("plan_research", "web_search")
builder.add_conditional_edges(
    "web_search", reseach_is_sufficient, ["plan_research", "build_outline"]
)
builder.add_conditional_edges("build_outline", fan_out_sections, ["draft_section"])
builder.add_edge("draft_section", "assemble_article")
builder.add_edge("assemble_article", "critique")
builder.add_conditional_edges(
    "critique", route_after_critique, ["draft_section", "final_polish"]
)
builder.add_edge("final_polish", END)

graph = builder.compile()
# graph.get_graph().draw_mermaid_png(output_file_path="flow.png")
