from clients import tavily_search
from logger import log_header, log_info, plural
from schemas import Source, State


def web_search(state: State) -> dict:
    log_header("Searching the Web")

    log_info(f"Running {plural(len(state['queries']), 'query', 'queries')}")

    sources: list[Source] = []
    seen: set[str] = set()

    for query in state["queries"]:
        log_info(f"Searching for: {query}")
        for hit in tavily_search.search(query, max_results=3)["results"]:
            if hit["url"] in seen:
                log_info(f"  Already seen: {hit['url']}")
                continue
            seen.add(hit["url"])
            log_info(f"  Found: {hit['title']} ({hit['url']})")
            sources.append(
                {
                    "id": len(sources) + 1,
                    "title": hit["title"],
                    "url": hit["url"],
                    "content": hit["content"],
                }
            )

    log_info(f"Collected {plural(len(sources), 'unique source')}")
    return {"sources": sources}
