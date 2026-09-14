import re
import unicodedata
from datetime import datetime
from pathlib import Path

from logger import log_header, log_success
from schemas import State

OUTPUT_DIR = Path("output")


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower())[:60].strip("-") or "article"


def final_polish(state: State) -> dict:
    log_header("Final Polish")

    sources = "\n".join(
        f"- [{s['id']}] {s['title']} - {s['url']}" for s in state["sources"]
    )
    document = f"# {state['topic']}\n\n{state['article']}\n\n## Sources\n\n{sources}\n"

    OUTPUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    path = OUTPUT_DIR / f"{slugify(state['topic'])}_{stamp}.md"
    path.write_text(document, encoding="utf-8")

    log_success(f"Article saved to {path}")
    return {"article": state["article"]}
