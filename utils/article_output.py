from logger import log_header, log_info


def print_article(result: dict, coverage: dict[str, int]) -> None:
    log_header(result["topic"])
    log_info(result["article"])
    log_info(f"{result['research_passes']} research_pass(es), coverage {coverage}")
    log_info(
        "Sources:\n"
        + "\n".join(f"[{s['id']}] {s['title']} - {s['url']}" for s in result["sources"])
    )
