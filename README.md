<div align="center">

# article-writer-langgraph

A [LangGraph](https://langchain-ai.github.io/langgraph/) pipeline that turns a topic into
a cited article. It researches the topic on the web, drafts the sections in parallel,
checks its own work and rewrites the sections that fail.

<img src="https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+">
<img src="https://img.shields.io/badge/LangGraph-1.2-1C3C3C?style=flat-square" alt="LangGraph">
<img src="https://img.shields.io/badge/search-Tavily-6366F1?style=flat-square" alt="Tavily">
<img src="https://img.shields.io/badge/uv-managed-DE5FE9?style=flat-square" alt="uv">
<img src="https://img.shields.io/badge/lint-ruff-D7FF64?style=flat-square" alt="Ruff">

</div>

---

```bash
uv run main.py "The history of Casio watches" "a technical reader"
```

## The flow

```
                    ┌───────────────────┐
                    │       START       │
                    └─────────┬─────────┘
                              ▼
            ┌─────────────────────────────────┐
            │  plan_research                  │◀─┐  topic + gaps ──▶ facets, queries
            └─────────────────┬───────────────┘  │
                              ▼                   │
            ┌─────────────────────────────────┐  │  queries ──▶ sources
            │  web_search                     │  │  (deduped by URL)
            └─────────────────┬───────────────┘  │
                              ▼                   │
                    ╔═══════════════════╗   gaps? └── another pass
                    ║ reseach_is_       ║   (router: coverage per facet
                    ║ sufficient        ║    below K distinct domains,
                    ╚═════════╦═════════╝    up to MAX_PASSES)
                              ▼
            ┌─────────────────────────────────┐
            │  build_outline                  │   sources ──▶ outline
            └─────────────────┬───────────────┘   (+ a word budget per section)
                              ▼
                    ╔═══════════════════╗
                    ║ fan_out_sections  ║   router: one Send per section
                    ╚═══════╦═══╦═══╦═══╝
                  ┌─────────┘   │   └─────────┐
                  ▼             ▼             ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
  ┌────────▶│  draft_   │ │  draft_   │ │  draft_   │   all at once
  │         │  section  │ │  section  │ │  section  │
  │         └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
  │               └─────────┐   │   ┌─────────┘
  │                         ▼   ▼   ▼
  │         ┌─────────────────────────────────┐
  │         │  assemble_article               │   drafts ──▶ article
  │         └─────────────────┬───────────────┘
  │                           ▼
  │         ┌─────────────────────────────────┐
  │         │  critique                       │   article ──▶ findings, scores
  │         └─────────────────┬───────────────┘   (citations, structure, length, tone)
  │                           ▼
  │                 ╔═══════════════════╗
  └─ blockers ──────║ route_after_      ║   router: redraft only the flagged
                    ║ critique          ║   sections, up to BUDGET passes
                    ╚═════════╦═════════╝
                              ▼
            ┌─────────────────────────────────┐
            │  final_polish                   │   article ──▶ output/<topic>_<time>.md
            └─────────────────┬───────────────┘
                              ▼
                    ┌───────────────────┐
                    │        END        │
                    └───────────────────┘
```

Three routers steer the graph:

- `reseach_is_sufficient` sends research back to `plan_research` while a facet is covered
  by fewer than `K` distinct domains, up to `MAX_PASSES` times.
- `fan_out_sections` sends every outlined section to `draft_section` at once.
- `route_after_critique` sends sections with blockers back to `draft_section`, this time
  with the old draft and the problems to fix. It stops when no blockers remain, after
  `BUDGET` passes, or when a pass stops reducing the failures.

`critique` runs these checks on the assembled article:

| Check | Rule | Severity |
| :-- | :-- | :-- |
| Citations | each `[id: "quote"]` cites a real source, and the quote appears in it | `blocker` if the source or quote is missing, `major` for a loose match or no citations |
| Structure | headings match the outline | `major` |
| Length | within 15% of `target_words` | `minor` |
| Tone | the model rates each section from 3 (no lapses) to 0 (wrong register throughout) | `blocker` at level 1 or below |

`final_polish` saves the article to `output/<topic>_<timestamp>.md`. LangGraph's own
render of the graph is in [`flow.png`](flow.png).

## Quickstart

You need Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <this-repo> && cd article-writer-langgraph
uv sync
```

Create a `.env` in the project root:

```ini
# provider:model, anything langchain's init_chat_model accepts
LLM_MODEL=openai:gpt-5.2
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

Then run it. Only the topic is required, and the arguments are positional:

```bash
uv run main.py "<topic>" "<audience>" "<tone>" <target_words>
# defaults: "a technical reader", "clear and direct", 800
```

To trace runs in LangSmith, add `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to `.env`.

## What a run looks like

Every step logs what it's doing. This is the critique loop from one run, abridged:

```
🚀 Critiquing the Article (pass 1)
ℹ️  Found 3 issues in structure, length, and citations
ℹ️  2. The G-Shock Gamble — tone level 1/3 (3 lapses)
⚠️  2 blockers found

🚀 Routing After Critique
ℹ️  Sending 1 section back for revision (pass 2/3):
ℹ️  Redrafting: The G-Shock Gamble — 3 problems to fix:
      • quote not in source 9: dropped from a third-floor bathroom window
      • tone level 1, 3 lapses: "Casio basically went full send on toughness"
      • 1043 words against a target of 800

🚀 Critiquing the Article (pass 2)
✅ No blockers found

🚀 Final Polish
✅ Article saved to output/the-history-of-casio-watches_20260914-161502.md
```

## Layout

```
main.py        CLI entrypoint
graph.py       StateGraph wiring
logger.py      colored console output
clients/       the LLM and Tavily clients
nodes/         one module per node or router
schemas/       Pydantic models and the graph State
utils/         the drafted reducer and the critique checks
tests/         pytest suite
output/        saved articles (gitignored)
```

## Development

```bash
uv run pytest           # test
uv run ruff check .     # lint
uv run ruff format .    # format
```
