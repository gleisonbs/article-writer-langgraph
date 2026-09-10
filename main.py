import sys

from graph import graph
from logger import log_success


def main() -> None:
    result = graph.invoke({"topic": sys.argv[1]})  # type: ignore

    print("\n")
    log_success(result["article"])
    for i, s in enumerate(result["sources"], start=1):
        print(f"[{i}] {s['title']} - {s['url']}")


if __name__ == "__main__":
    main()
