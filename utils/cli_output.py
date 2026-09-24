import json

from logger import log_header, log_info, log_list, log_success, log_warning, plural


def show_proposal(proposal: dict) -> None:
    log_header("Proposed Outline")
    sources_by_id = {s["id"]: s for s in proposal["sources"]}
    for section in proposal["outline"]:
        log_info(f"{section['index']}. {section['heading']}")
        sources = [sources_by_id[sid] for sid in section["source_ids"]]
        log_list([f"[{s['id']}] {s['title']} - {s['url']}" for s in sources])

    coverage = ", ".join(f"{facet}: {plural(n, 'domain')}" for facet, n in proposal["coverage"].items())
    log_info(f"Coverage — {coverage}")


def display_formatted_outline(state: dict) -> None:
    print(json.dumps([o.model_dump() for o in state["outline"]], indent=2))
    

def print_report(state: dict) -> None:
    print(state["article"])

    log_header("Critique Passes")
    for score in state["scores"]:
        failures, tone = score["failures"], score["tone"]
        message = f"pass {score['pass']}: {plural(failures, 'verifiable failure')}, tone {tone}/3"
        if failures or tone <= 1:
            log_warning(message)
        else:
            log_success(message)

    log_header("Sources")
    for source in state["sources"]:
        log_info(f"[{source['id']}] {source['title']} - {source['url']}")
