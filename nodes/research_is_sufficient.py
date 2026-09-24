from collections import defaultdict
from urllib.parse import urlsplit

from schemas import State

MAX_PASSES = 1
MIN_DOMAIN_COUNT = 1


def domains_per_facet(state: State) -> dict[str, int]:
    """Distinct DOMAINS per facet - three pages from one site is one opinion"""
    hosts = defaultdict(set)
    for source in state["sources"]:
        host = urlsplit(source["url"]).hostname or ""
        for facet in source["facets"]:
            hosts[facet].add(host)
    return {facet: len(hosts[facet]) for facet in state["facets"]}


def facets_below_min_domain_count(state: State) -> list[str]:
    return [facet for facet, domain_count in domains_per_facet(state).items() 
            if domain_count < MIN_DOMAIN_COUNT]


def reseach_is_sufficient(state: State) -> str:
    if not facets_below_min_domain_count(state) or state["research_passes"] >= MAX_PASSES:
        return "build_outline"
    return "plan_research"
