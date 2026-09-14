from collections import defaultdict
from urllib.parse import urlsplit

from schemas import State

K, MAX_PASSES = 2, 3


def coverage(state: State) -> dict[str, int]:
    """Distinct DOMAINS per facet - three pages from one site is one opinion"""
    hosts = defaultdict(set)
    for s in state["sources"]:
        host = urlsplit(s["url"]).hostname or ""
        for facet in s["facets"]:
            hosts[facet].add(host)
    return {f: len(hosts[f]) for f in state["facets"]}


def gaps_in(state: State) -> list[str]:
    return [f for f, n in coverage(state).items() if n < K]


def reseach_is_sufficient(state: State) -> str:
    if not gaps_in(state) or state["research_passes"] >= MAX_PASSES:
        return "build_outline"
    return "plan_research"
