# Athenah AI

A hybrid RAG framework for codebases. Athenah combines:

- a **vector store** (ChromaDB) for semantic search,
- a **symbol index** for O(1) exact lookups, and
- a **knowledge graph** (NetworkX) for structural relationships (call graphs, inheritance),

driven by **tree-sitter** AST parsing for C++, Python, TypeScript, and JavaScript. On top of the index sits a multi-provider LLM client (OpenAI, Anthropic, xAI).

## Features

- **Hybrid retrieval** — vector + symbol + graph queries, not just embeddings
- **Multi-language AST parsing** — C++, Python, TypeScript, JavaScript
- **Multi-LLM client** — OpenAI, Anthropic, xAI behind one adapter interface
- **Storage** — local filesystem or Google Cloud Storage
- **Code labeler** — generates `.ai.json` / `.ai.md` metadata for source files
- **Formal modeler** — closure-gated LLM extraction of finite state machines from real C++, with a differential fidelity gate against the actual implementation (see [`athenah_ai/modeler/FINDING.md`](athenah_ai/modeler/FINDING.md))
- **Atlas** — a personal job/life knowledge graph (identities, orgs, repos, servers, workflows, rules) over hand-editable YAML facts; renders the bootstrap context any zero-context AI agent needs (see below)

## Requirements

- Python ≥ 3.10.6
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

```bash
git clone https://github.com/transia/athenah-ai.git
cd athenah-ai
poetry install
```

## Configuration

Copy `.env.sample` to `.env` and fill in keys for the providers you intend to use:

```env
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
XAI_API_KEY=...
EMBEDDING_MODEL=text-embedding-3-large
CHUNK_SIZE=1000
GCP_INDEX_BUCKET=             # only for storage_type="gcs"
```

For GCS storage, also set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`.

## Quick Start

### Index a codebase

```python
from athenah_ai.indexer import IndexClient

indexer = IndexClient(
    storage_type="local",   # or "gcs"
    id="my-project",
    dir="workspace",
    name="myapp",
    version="v1",
)
indexer.build_from_dirs(
    source="/path/to/project",
    dirs=["src", "include"],
    include_root=False,
    clean_dirs=True,
)
```

### Query the index

```python
result = indexer.query("How does the consensus algorithm work?", limit=10)
for r in result.results:
    print(r["source"], r["score"])

# Exact symbol lookup
syms = indexer.find_symbol("STAmount")

# Structural queries
callers = indexer.find_callers("submit")
graph = indexer.get_call_graph("STAmount", max_depth=2)
```

### Ask an LLM with RAG

```python
from athenah_ai.client import AthenahClient

client = AthenahClient(
    id="my-project",
    provider="openai",          # "openai" | "anthropic" | "xai"
    model_group="workspace",
    custom_model="myapp",
    version="v1",
    model_name="gpt-4.1",
    temperature=0,
)

print(client.ask("What is STAmount?"))
```

If a vector store has been loaded for `custom_model`, `ask()` automatically retrieves context. Otherwise it falls back to the base LLM.

## Modeler — LLM-extracted formal models

Schema-forced FSM extraction from real C++ source, paired with a differential
fidelity gate against the actual implementation. The pipeline is
general-purpose; `ripple::LedgerTrie` is the proof-of-concept target.

**Reproduce the banked result** (no LLM calls; uses the committed FSM
artefact, builds the standalone C++ harness with plain clang++):

```bash
bash athenah_ai/modeler/reproduce.sh
# test_insert  : 0 / 4   ( 0.0%)
# test_support : 4 / 31  (12.9%)
```

**Extract an FSM for any C++ file:**

```bash
poetry run python -m athenah_ai.modeler.extractor \
    --source-root <abs/path/to/repo> \
    --target <relative/path/to/Foo.h> \
    --out athenah_ai/modeler/artifacts/foo.fsm.json
```

The schema (`schema.py`) enforces closure — no undefined helpers, no
prose-in-JSON. The extractor (`extractor.py`) stages structure + parallel
per-unit decomposition with a validator-driven repair loop and raw-output
caching. See [`athenah_ai/modeler/FINDING.md`](athenah_ai/modeler/FINDING.md)
for the full write-up: what the experiment proved, what it did not, and where
the real cost actually lands in LLM-driven formal-methods work.

## Atlas — agent bootstrap knowledge graph

`athenah_ai/atlas/` encodes the operator's world as a typed graph: identities
and their GitHub capabilities, orgs, repos (keyed by remote, not directory),
local checkouts/worktrees, servers, deploy workflows, rules, and plan stores.
Source of truth is hand-editable YAML under `athenah_ai/atlas/facts/`
(taught facts) plus scanner-maintained `facts/derived/` (never clobbers
taught facts).

```bash
python -m athenah_ai.atlas scan                 # rescan ~/projects checkouts
python -m athenah_ai.atlas context --cwd .      # scoped bootstrap for a dir
python -m athenah_ai.atlas render               # write full ATLAS.md
python -m athenah_ai.atlas render --claude-md   # emit generated CLAUDE.md
python -m athenah_ai.atlas render --skills-dir ~/.claude/skills   # one rule-<slug> skill per conditional rule
python -m athenah_ai.atlas teach --edge can_write identity:github/x org:y
python -m athenah_ai.atlas why identity:github/x   # provenance of any fact
python -m athenah_ai.atlas sync                    # re-render all consumers
```

`teach` and `scan` auto-sync every configured consumer (global CLAUDE.md,
ATLAS.md, downstream repo copies — see `AtlasConfig.sync_targets`) when run
against the default facts dir; sandboxed facts dirs skip it unless `--sync`.

Seed inventory: `athenah_ai/atlas/seeds/taught.yaml`
(`teach --import` it once, then `scan`).

## Project layout

```
athenah_ai/
  client/        # AthenahClient + LLM adapters (OpenAI / Anthropic / xAI)
  indexer/       # Hybrid index: vector + symbol + knowledge graph
  labeler/       # File-level .ai.json / .ai.md generation
  agent/         # LangGraph agent scaffolding
  modeler/       # Experimental: LLM-extracted formal models (see FINDING.md)
  config.py      # Centralized configuration
```

## Development

```bash
poetry install
poetry run flake8 .
poetry run pytest tests/
```

## License

MIT — see [LICENSE](LICENSE).

## Contact

Denis Angell — <dangell@transia.co>
