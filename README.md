<div align="center">

# 📰 article-writer-langgraph

A [LangGraph](https://langchain-ai.github.io/langgraph/) pipeline that turns a topic into
a cited article. It plans its own search queries, gathers sources from the web, outlines
the piece, and drafts every section in parallel.

<img src="https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12+">
<img src="https://img.shields.io/badge/LangGraph-1.2-1C3C3C?style=flat-square" alt="LangGraph">
<img src="https://img.shields.io/badge/search-Tavily-6366F1?style=flat-square" alt="Tavily">
<img src="https://img.shields.io/badge/uv-managed-DE5FE9?style=flat-square" alt="uv">
<img src="https://img.shields.io/badge/lint-ruff-D7FF64?style=flat-square" alt="Ruff">

</div>

---

```bash
uv run main.py "The history of Casio watches"
```

## 🔀 The flow

```
                    ┌───────────────────┐
                    │       START       │
                    └─────────┬─────────┘
                              ▼
            ┌─────────────────────────────────┐
            │  plan_research                  │   topic ──▶ 3-6 queries
            └─────────────────┬───────────────┘
                              ▼
            ┌─────────────────────────────────┐
            │  web_search                     │   queries ──▶ sources
            └─────────────────┬───────────────┘        (deduped by URL)
                              ▼
            ┌─────────────────────────────────┐
            │  build_outline                  │   sources ──▶ outline
            └─────────────────┬───────────────┘
                              ▼
                    ╔═══════════════════╗
                    ║ fan_out_sections  ║   router: one Send per section
                    ╚═══════╦═══╦═══╦═══╝
                  ┌─────────┘   │   └─────────┐
                  ▼             ▼             ▼
            ┌───────────┐ ┌───────────┐ ┌───────────┐
            │  draft_   │ │  draft_   │ │  draft_   │   all at once
            │  section  │ │  section  │ │  section  │
            └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
                  └─────────┐   │   ┌─────────┘
                            ▼   ▼   ▼
            ┌─────────────────────────────────┐
            │  assemble_article               │   drafts ──▶ article
            └─────────────────┬───────────────┘        (sorted by index)
                              ▼
                    ┌───────────────────┐
                    │        END        │
                    └───────────────────┘
```

`fan_out_sections` is a router rather than a node. It emits one LangGraph `Send` per
outlined section, so all the sections get drafted at the same time. Those drafts land
back in `State.drafted`, which uses an `operator.add` reducer so the parallel writes
accumulate instead of overwriting each other. They finish in whatever order they finish,
so `assemble_article` sorts by `index` before joining them.

<details>
<summary>📐 <b>Rendered graph</b></summary>

<br>

LangGraph can draw the compiled graph itself. The current render lives in
[`flow.png`](flow.png):

<div align="center"><img src="flow.png" alt="Compiled LangGraph flow" width="180"></div>

Regenerate it with:

```python
from graph import graph

graph.get_graph().draw_mermaid_png(output_file_path="flow.png")
```

</details>

## ⚡ Quickstart

You need Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone <this-repo> && cd article-writer-langgraph
uv sync
```

Drop a `.env` in the project root:

```ini
# provider:model, anything langchain's init_chat_model accepts
LLM_MODEL=openai:gpt-5.2

# the key for whichever provider LLM_MODEL names
OPENAI_API_KEY=sk-...

# web search
TAVILY_API_KEY=tvly-...
```

Then write something:

```bash
uv run main.py "How mechanical keyboards got popular again"
```

<details>
<summary>🔭 <b>Optional: LangSmith tracing</b></summary>

<br>

Add these to `.env` to trace every run:

```ini
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=article-writer

# only if you are not on the US cloud. Defaults to https://api.smith.langchain.com
# LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com
```

</details>

## 📺 What a run looks like

Every step announces itself, so you can watch the article get built:

```
============================================================
🚀 Planning Research
============================================================

ℹ️  Topic: The history of Casio watches
ℹ️  Asking the model for search queries
ℹ️  Planned 5 queries:
ℹ️    • history of Casio watches timeline key milestones
ℹ️    • best-selling Casio watch models F-91W G-Shock A168

============================================================
🚀 Searching the Web
============================================================

ℹ️  Running 5 queries
ℹ️  Searching for: history of Casio watches timeline key milestones
ℹ️    Found: Casio - Wikipedia (https://en.wikipedia.org/wiki/Casio)
ℹ️    Already seen: https://en.wikipedia.org/wiki/Casio
ℹ️  Collected 12 unique sources

============================================================
🚀 Building the Outline
============================================================

ℹ️  Cataloging 12 sources
ℹ️  Outlined 4 sections:
ℹ️    1. From Calculators to Timepieces (sources 1, 4, 7)

============================================================
🚀 Dispatching Sections
============================================================

ℹ️  Sending 4 sections off to be drafted:
ℹ️    1. From Calculators to Timepieces — 3 sources

...

============================================================
🚀 Assembling the Article
============================================================

ℹ️  Putting 4 sections in order:
ℹ️  Article is ready (7213 characters)
```

The finished article prints at the end, followed by a numbered source list matching the
inline `[n]` citations.

## 🗂️ Layout

One module per thing. Each package re-exports its public names, so imports stay flat:
`from nodes import plan_research`, `from schemas import State`.

```
main.py              CLI entrypoint: topic in, article out
graph.py             StateGraph wiring, exports the compiled `graph`
logger.py            colored console output
```

<table>
<tr><th align="left" colspan="2">📡 <code>clients/</code>, one module per external client</th></tr>
<tr><td><code>llm.py</code></td><td><code>model</code>, from langchain's <code>init_chat_model</code></td></tr>
<tr><td><code>search.py</code></td><td><code>tavily_search</code>, a <code>TavilyClient</code></td></tr>
</table>

<table>
<tr><th align="left" colspan="2">⚙️ <code>nodes/</code>, one module per graph node</th></tr>
<tr><td><code>plan_research.py</code></td><td>topic → queries</td></tr>
<tr><td><code>web_search.py</code></td><td>queries → sources</td></tr>
<tr><td><code>build_outline.py</code></td><td>sources → outline</td></tr>
<tr><td><code>fan_out_sections.py</code></td><td>outline → <code>Send</code>s <i>(router)</i></td></tr>
<tr><td><code>draft_section.py</code></td><td>section → drafted section</td></tr>
<tr><td><code>assemble_article.py</code></td><td>drafts → article</td></tr>
</table>

<table>
<tr><th align="left" colspan="2">🧬 <code>schemas/</code>, one module per type</th></tr>
<tr><td><code>state.py</code></td><td><code>State</code>, the graph state</td></tr>
<tr><td><code>source.py</code></td><td><code>Source</code></td></tr>
<tr><td><code>search_queries.py</code></td><td><code>SearchQueries</code></td></tr>
<tr><td><code>section.py</code></td><td><code>Section</code></td></tr>
<tr><td><code>outline.py</code></td><td><code>Outline</code></td></tr>
<tr><td><code>section_task.py</code></td><td><code>SectionTask</code>, the payload <code>draft_section</code> receives</td></tr>
</table>

## 🧠 State

| Key | Written by | Notes |
| :-- | :-- | :-- |
| `topic` | the caller | the input |
| `queries` | `plan_research` | 3-6 search queries |
| `sources` | `web_search` | deduplicated by URL, ids assigned in order |
| `outline` | `build_outline` | 3-6 sections, each naming the source ids it needs |
| `drafted` | `draft_section` | `operator.add` reducer, so parallel drafts accumulate |
| `article` | `assemble_article` | sections sorted by `index`, joined under `##` headings |

## 🛠️ Development

```bash
uv run ruff check .     # lint
uv run ruff format .    # format
```
