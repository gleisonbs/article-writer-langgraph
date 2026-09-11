import sys

from graph import graph
from logger import log_success

from nodes import coverage

def main() -> None:
    result = graph.invoke({
        "topic": sys.argv[1],
        "audience": sys.argv[2] if len(sys.argv) > 2 else "a technical reader",
        "facets": [], "queries": [], "query_log": [],
        "sources": [], "research_passes": 0,
    })  # type: ignore

    print("\n")
    print(f"# {result['topic']}\n")
    print(result["article"])
    print(f"\n-- {result["research_passes"]} research_pass(es), "
          f"coverage {coverage(result)}") # type: ignore
    print("\n## Sources")
    for i, s in enumerate(result["sources"], start=1):
        print(f"[{i}] {s['title']} - {s['url']}")


if __name__ == "__main__":
    main()
