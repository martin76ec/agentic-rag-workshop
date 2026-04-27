<!-- docmancer:start -->
# docmancer

Docmancer compresses documentation context so coding agents spend tokens on code, not on rereading raw docs. Docs are fetched from public sites, indexed locally with SQLite FTS5, and returned as compact context packs with source attribution. No API keys, no vector database, no background daemons on the core path.

**MIT open source.** Everything runs locally. An optional benchmarking harness (`docmancer bench`) compares retrieval backends on your own corpus.

Executable: `/Users/martin/.local/pipx/venvs/docmancer/bin/docmancer --config /Users/martin/.docmancer/docmancer.yaml`

**All commands below use `docmancer` as shorthand for the full executable path above.**

Use docmancer when the user asks about library docs, API references, vendor docs, version-specific behavior, offline docs, or wants to add docs before answering a technical question.

## Workflow

1. Run `docmancer list` to see indexed docs.
2. Run `docmancer query "question"` when relevant docs are present.
3. If docs are missing and the user approves the source, run `docmancer add <url-or-path>` to index it locally.
4. Use the returned sections as source-grounded context for the answer or code change.

## Core commands

```bash
docmancer setup
docmancer add https://docs.example.com
docmancer add ./docs
docmancer update
docmancer query "how to authenticate"
docmancer query "how to authenticate" --limit 10
docmancer query "how to authenticate" --expand
docmancer query "how to authenticate" --expand page
docmancer query "how to authenticate" --format json
docmancer list
docmancer inspect
docmancer remove <source>
docmancer doctor
docmancer fetch <url> --output <dir>
```

`query` prints estimated raw docs tokens, context-pack tokens, percent saved, and agentic runway. Prefer the compact default. Use `--expand` for adjacent sections; use `--expand page` only when the surrounding page is necessary.

`add` supports documentation URLs, GitHub repositories with README and docs markdown, local directories, markdown files, and text files. Extracted markdown/json remains inspectable under the configured `.docmancer/extracted` directory.

## Benchmarking retrieval (optional)

The `bench` namespace compares retrieval backends (FTS, vector, and an RLM path) on the same corpus and question set. FTS ships in core; the others are experimental extras.

```bash
docmancer bench init
docmancer bench dataset use lenny                                          # built-in zero-config dataset (fetched once, then cached)
docmancer bench dataset create --from-corpus <dir> --size 30 --name <name> --provider auto
docmancer bench dataset validate <path>
docmancer bench run --backend fts --dataset <name>
docmancer bench compare <run_id_a> <run_id_b>
docmancer bench report <run_id>
docmancer bench list
docmancer bench dataset list-builtin
```

Artifacts live under `.docmancer/bench/runs/<run_id>/`. A content-hashed `ingest_hash` stops `bench compare` from mixing runs against drifted corpora unless you pass `--allow-mixed-ingest`.

Experimental backends require optional extras:

- `pipx install 'docmancer[vector]'`
- `pipx install 'docmancer[rlm]'`
- `pipx install 'docmancer[judge]'`

When documentation context is relevant, do not rely only on model memory or latest-only hosted docs. Query docmancer first, then cite or summarize the relevant local sections in the response.
<!-- docmancer:end -->

# Coding Principles

## TDD (Test-Driven Development)

- **Red-Green-Refactor**: write a failing test first, make it pass with the minimum code, then refactor
- **One assertion per test** — test one behavior; descriptive name using `given_when_then` or `should` pattern
- **Run the test suite** before any commit or PR
- **No production code without a corresponding test** — exceptions: config files, build scripts, trivial getters/setters
- Tests are **specifications**, not afterthoughts — if the test is hard to write, the design is wrong

## DDD (Domain-Driven Design)

- **Ubiquitous language** — class/module names, methods, and variables must match the domain terminology used by stakeholders and other teams
- **Domain entities stay clean** — no framework annotations, no ORM coupling, no infrastructure concerns inside domain objects
- **Value objects** for any primitive that carries meaning (`Email`, `Money`, `UserId`, `DateRange`)
- **Repositories** abstract persistence — domain code never touches the DB directly
- **Domain services** hold behavior that doesn't naturally belong on a single entity
- **Anti-corruption layer** at bounded-context boundaries — translate between internal and external models

## Python Package Management

- **Use `uv` exclusively** — never use `pip`, `uv pip`, or any other Python package manager directly
- **Always work inside a virtual environment** — run `uv sync` or `uv venv` first; never install packages globally or into the system Python
- Install packages with `uv add <package>` (adds to `pyproject.toml` and installs into the venv)
- Run tools/scripts with `uv run <command>` to ensure the venv is activated
- If a venv does not exist, create one with `uv venv` before any other operation

## Healthy Code Principles

- **Function size**: max ~15–20 lines. If longer, extract helpers with clear names.
- **Early returns**: return early from functions to flatten nesting and eliminate `else` chains
- **Short ifs**: simple guards and assignments may use ternary or single-line returns; never nest beyond 2 levels — extract or invert
- **No magic numbers or strings**: extract to named constants or enums — every literal must explain itself
- **Single Responsibility**: one function, one job. If you use "and" to describe what it does, split it.
- **No commented-out code**: delete it. Git history has the original. If it's an explanation, write a clear name instead.
- **Consistent naming**:
  - `is`/`has` prefixes for booleans (`isActive`, `hasPermission`)
  - Verbs for methods (`getUser`, `validateOrder`)
  - Nouns for classes and entities (`Order`, `InvoiceService`)
  - Avoid abbreviations (unless universally known: `id`, `html`, `db`)
- **Side effects at edges**: pure logic in the middle, side effects (IO, DB, network, logging) at the application boundary
- **No silent catches**: every caught exception must log, rethrow wrapped, or return a meaningful error — never swallow
- **Immutable by default**: prefer `const`, `readonly`, `final` — mutate only when performance demands it and document why
