from clients import tavily_search
from logger import log_header, log_info, plural
from schemas import Source, State


def web_search(state: State) -> dict:
    log_header("Searching the Web")

    log_info(f"Running {plural(len(state['queries']), 'query', 'queries')}")

    seen = {s["url"] for s in state["sources"]}
    first_id = len(state["sources"]) + 1
    sources: list[Source] = []

    for planned_query in state["queries"]:
        log_info(f"Searching for: {planned_query.query}  [{planned_query.facet}]")
        for hit in tavily_search.search(planned_query.query, max_results=3)["results"]:
            if hit["url"] in seen:
                log_info(f"  Already seen: {hit['url']}")
                continue
            seen.add(hit["url"])
            log_info(f"  Found: {hit['title']} ({hit['url']}) [{planned_query.facet}]")
            sources.append(
                {
                    "id": first_id + len(sources),
                    "title": hit["title"],
                    "url": hit["url"],
                    "content": hit["content"],
                    "facets": [planned_query.facet],
                }
            )

    log_info(
        f"Collected {plural(len(sources), 'new source')} "
        f"({len(state['sources']) + len(sources)} total)"
    )
    return {"sources": sources, "query_log": [q.query for q in state["queries"]]}
