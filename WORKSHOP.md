<!-- ════════════════════════════════════════════════════════════════════════ -->
<!--                          ✦   HEADER BANNER   ✦                          -->
<!-- ════════════════════════════════════════════════════════════════════════ -->

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,6&height=240&section=header&text=The%20Workshop&fontSize=64&fontColor=ffffff&fontAlignY=38&desc=Build%20a%20RAG.%20Then%20learn%20when%20to%20bend%20it.&descAlignY=62&descSize=16&animation=fadeIn" alt="Workshop banner" width="100%"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=2800&pause=900&color=06B6D4&center=true&vCenter=true&width=720&lines=Two+tracks.+Same+incident.;Track+A+%E2%86%92+build+RAG+from+broken+code.;Track+B+%E2%86%92+compare+architectures+and+measure.;Run+it+%E2%86%92+observe+it+%E2%86%92+break+it+%E2%86%92+rebuild+it." alt="Typing tagline"/>

<br/><br/>

<img src="https://img.shields.io/badge/⏱%20duration-~6%20hours-8B5CF6?style=for-the-badge&labelColor=0f0f1e" alt="duration"/>
<img src="https://img.shields.io/badge/📚%20parts-7-06B6D4?style=for-the-badge&labelColor=0f0f1e" alt="parts"/>
<img src="https://img.shields.io/badge/🧠%20level-beginner→intermediate-EC4899?style=for-the-badge&labelColor=0f0f1e" alt="level"/>
<img src="https://img.shields.io/badge/🛠%20prereq-make%20setup%20%26%26%20make%20seed-F43F5E?style=for-the-badge&labelColor=0f0f1e" alt="prereqs"/>

<br/>

<a href="WORKSHOP.es.md"><img src="https://img.shields.io/badge/🇪🇸%20Leer%20en%20Español-1a1a2e?style=for-the-badge&labelColor=0f0f1e" alt="Leer en Español"/></a>

<br/><br/>

[🎬&nbsp;Briefing](#briefing) &nbsp;•&nbsp;
[A1&nbsp;Plain](#a1-plain) &nbsp;•&nbsp;
[A2&nbsp;Graph](#a2-graph) &nbsp;•&nbsp;
[A3&nbsp;Agentic](#a3-agentic) &nbsp;•&nbsp;
[B4&nbsp;Compare](#b4-compare) &nbsp;•&nbsp;
[B5&nbsp;Eval](#b5-eval) &nbsp;•&nbsp;
[B6&nbsp;Iterate](#b6-iterate) &nbsp;•&nbsp;
[B7&nbsp;Endgame](#b7-endgame)

</div>

<br/>

<a id="briefing"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,16,6&height=56&section=header&text=Briefing&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=An%20on-call%20incident%20lands%20in%20your%20lap%20at%203am&descAlignY=68&descSize=13&descColor=e2e2e2" alt="Briefing"/>

<div align="center">

<table>
  <tr>
    <td align="center" width="120">
      <img src="https://img.icons8.com/fluency/72/error.png" width="56" alt=""/>
    </td>
    <td>
      <b>📟 PagerDuty just woke you up.</b><br/>
      <code>kafka-broker</code> is returning 5xx errors. Consumer lag is growing.<br/>
      Services are failing to connect. <b>It's 3am. You're on-call.</b>
    </td>
  </tr>
</table>

</div>

Your job: figure out **what broke**, **what else is at risk**, and **what to do about it** —
and along the way build the RAG system that helps you do it.

This workshop has two tracks that share the same incident scenario:

| Track | What you do | For whom | Time |
|:--|:--|:--|:--|
| **A — Build it** | Fix three deliberately broken RAG implementations. Each part ships runnable-but-bad code. You diagnose, fix the TODOs, and watch the metrics improve. | RAG beginners | ~3 h |
| **B — Compare it** | Run the reference implementation in three modes side by side. Measure retrieval quality. Iterate on prompts and topology. | Intermediates | ~3 h |

> [!IMPORTANT]
> **Carry this question through every part:**
> *What does the system know now that it didn't know in the previous step — and how does that change the response?*

<br/>

---

# 🛠️ Track A — Build it

You ship a RAG that "kinda works." Each part identifies a different failure
mode and you fix it. The exercise files live in `exercises/part1_plain/`,
`exercises/part2_graph/`, and `exercises/part3_agentic/`.

```bash
make exercise 1.1     # show the broken output, then run the tests
make verify   1.1     # only run the tests
make solution 1.1     # reveal which file in src/ is the reference
```

<br/>

<a id="a1-plain"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=11,6,20&height=56&section=header&text=A1%20%E2%80%94%20Plain%20RAG%20(it's%20broken%2C%20fix%20it)&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20chunking%20%C2%B7%20top-k%20%C2%B7%20prompt%20construction&descAlignY=68&descSize=13&descColor=e2e2e2" alt="A1 — Plain RAG"/>

<img src="https://img.shields.io/badge/exercises-3-06B6D4?style=flat-square&labelColor=0f0f1e"/>
<img src="https://img.shields.io/badge/concepts-chunking%20%C2%B7%20top--k%20%C2%B7%20prompt-06B6D4?style=flat-square&labelColor=0f0f1e"/>

The starter ships a Plain RAG with three problems that any new RAG runs into.
You'll feel each one in the LLM's output before you fix it.

| # | What's broken | What you'll learn |
|:--|:--|:--|
| **1.1** | Each service is one giant chunk. Search returns the right service for any query, but the embedding can't tell "what does Kafka *do*?" from "what *depends on* Kafka?". | Why sectioned chunks matter; how chunk shape changes recall. |
| **1.2** | `top_k=1` and no metadata filter. Department-knowledge entries leak into service results. | Tuning k; using `filters` to scope; per-field filtering. |
| **1.3** | The system prompt mentions "context" but never templates the retrieved chunks into the user message. The LLM is left ungrounded. | Prompt construction; structured context blocks. |

<details>
  <summary><b>How to run each fix</b></summary>
  <br/>

```bash
# 1.1 — Chunking
make exercise 1.1
# Edit exercises/part1_plain/chunking.py, fix the TODOs.
make verify 1.1

# 1.2 — Top-k and metadata filtering
make exercise 1.2
# Edit exercises/part1_plain/search.py.
make verify 1.2

# 1.3 — Prompt construction
make exercise 1.3
# Edit exercises/part1_plain/prompt.py.
make verify 1.3
```

Pistas tiered: `exercises/part1_plain/hints.md`. Reveal one at a time.

</details>

> [!TIP]
> Before fixing 1.1, read what `chunk_service()` returns and ask: which queries
> would NEVER match the right hit? That tells you where to split.

<br/>

<a id="a2-graph"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=6,11,20&height=56&section=header&text=A2%20%E2%80%94%20Graph%20RAG%20(it's%20broken%2C%20fix%20it)&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=60%20min%20%E2%80%94%20Cypher%20%C2%B7%20variable-length%20paths%20%C2%B7%20fusion&descAlignY=68&descSize=13&descColor=e2e2e2" alt="A2 — Graph RAG"/>

<img src="https://img.shields.io/badge/exercises-3-8B5CF6?style=flat-square&labelColor=0f0f1e"/>
<img src="https://img.shields.io/badge/concepts-Cypher%20%C2%B7%20paths%20%C2%B7%20fusion-8B5CF6?style=flat-square&labelColor=0f0f1e"/>

Plain RAG is fixed but the LLM still says *"may affect downstream services"*
in vague terms. The cascade is in Neo4j — you just never queried it.

| # | What's broken | What you'll learn |
|:--|:--|:--|
| **2.1** | The neighborhood query returns the service's own props but not its dependencies. | Cypher MATCH/OPTIONAL MATCH; `collect(DISTINCT ...)`. |
| **2.2** | The blast-radius query only finds depth-1 dependents. Cascades like `kafka → clickhouse → tracker` are invisible. | Variable-length paths `*1..N`; binding to `path` and returning nodes. |
| **2.3** | Vector context and graph context are concatenated as a wall of text. The LLM ignores the graph because it's at the bottom and unstructured. | Priority-ordered fusion; structured prompt sections. |

<details>
  <summary><b>Verify the cascade in Neo4j browser</b></summary>
  <br/>

```cypher
MATCH path = (aff:Service)-[:DEPENDS_ON*1..4]->(root:Service {name: 'kafka-broker'})
RETURN path
```

You should see kafka at the center with chains radiating outward.

</details>

<br/>

<a id="a3-agentic"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,6,11&height=56&section=header&text=A3%20%E2%80%94%20Agentic%20RAG%20(it's%20broken%2C%20fix%20it)&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=75%20min%20%E2%80%94%20triage%20%C2%B7%20router%20%C2%B7%20state%20%C2%B7%20specialist&descAlignY=68&descSize=13&descColor=e2e2e2" alt="A3 — Agentic RAG"/>

<img src="https://img.shields.io/badge/exercises-4-EC4899?style=flat-square&labelColor=0f0f1e"/>
<img src="https://img.shields.io/badge/concepts-classifier%20%C2%B7%20routing%20%C2%B7%20state%20%C2%B7%20expertise-EC4899?style=flat-square&labelColor=0f0f1e"/>

Plain + Graph RAG already give precise context, but the LLM still applies
the same generic prompt to every incident. The agentic phase fixes that —
classify, route, then run a specialist with department-specific knowledge.

| # | What's broken | What you'll learn |
|:--|:--|:--|
| **3.1** | The triage classifier always returns `platform` because the LLM's JSON arrives wrapped in markdown fences and the parser doesn't tolerate it. | Defensive JSON parsing; enum coercion. |
| **3.2** | The router picks a specialist by regexing the service name, ignoring the blast-radius report. Cross-department incidents are silent. | Reading state in LangGraph; flagging multi-team blast. |
| **3.3** | The shared state TypedDict only carries `messages`. Specialists receive empty context. | Designing agent state; what each node reads/writes. |
| **3.4** | The data specialist's system prompt is generic — same as platform's. No expertise leaks through. | Per-role system prompts; concrete operational language. |

> [!NOTE]
> **The "agentic" moment.** Once 3.1–3.3 are green, the router's decision is
> driven by `blast_radius_report.affected_departments`, which was retrieved
> from Neo4j by the triage agent. **Retrieval informs routing, which
> determines what gets retrieved next.** That feedback loop is what makes
> the system "agentic" rather than a static pipeline.

<br/>

> [!TIP]
> **Take a 20-minute break.** Track B is much less typing — perfect for after coffee.

<br/>

---

# 📊 Track B — Compare it

Track A built a working RAG. Track B benchmarks it against the reference
implementation in `src/`, measures retrieval quality on a gold set, and
iterates on prompts and topology.

```bash
make rag       kafka-broker     # Plain RAG (vector only)
make graph-rag kafka-broker     # Graph RAG (+ Neo4j)
make tui       kafka-broker     # Agentic RAG (full pipeline)
make eval                       # Run retrieval-quality metrics
```

<br/>

<a id="b4-compare"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=11,6,20&height=56&section=header&text=B4%20%E2%80%94%20Three%20modes%20side%20by%20side&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=30%20min%20%E2%80%94%20same%20incident%2C%20three%20architectures&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B4 — Compare"/>

Run the same incident through all three modes in separate terminals:

```bash
make rag kafka-broker        # 🔵 Plain
make graph-rag kafka-broker  # 🟣 Graph
make tui kafka-broker        # 🌈 Agentic
```

<div align="center">

| Question | Plain | Graph | Agentic |
|:--|:--:|:--:|:--:|
| Which services are at risk? | Vague | Exact (5 named) | Exact + departments |
| Who should be paged? | Generic | Generic | `data-oncall` specifically |
| What Kafka command to run? | Unlikely | Unlikely | Likely (specialist knows) |
| LLM calls | `1` | `1` | `2` |
| Retrieval steps | `1` | `3` | `4–5` |

</div>

<br/>

<a id="b5-eval"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=6,11,20&height=56&section=header&text=B5%20%E2%80%94%20Measure%20retrieval%20quality&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20gold%20set%2C%20recall%40k%2C%20precision%40k%2C%20MRR&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B5 — Eval"/>

Architecture comparisons are subjective until you have metrics. The
evaluation harness in `eval/` runs a 15-query gold set against any
retriever and computes:

- **Recall@k** — fraction of expected services that appear in top-k
- **Precision@k** — fraction of top-k that were expected
- **MRR** (Mean Reciprocal Rank) — rewards ranking the right thing first

```bash
make eval                              # default: vector mode, k=5
make eval MODE=graph                   # vector + Neo4j fusion
make eval MODE=graph K=10              # wider top-k
```

<details>
  <summary><b>Read the gold set</b></summary>
  <br/>

`eval/gold_set.json` contains 15 `(query, expected_services)` pairs covering
all 5 departments. Each query is the kind of thing an on-call would type at
3 AM. Add your own — it's just JSON.

</details>

> [!TIP]
> Run `make eval` *before* and *after* you implement Track A's exercise 1.2
> (top-k + filtering). The recall lift is the most direct evidence that the
> fix matters.

<br/>

<a id="b6-iterate"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,16,6&height=56&section=header&text=B6%20%E2%80%94%20Iterate%20on%20prompts%20and%20topology&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20break%20things%20on%20purpose%2C%20see%20what%20bends&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B6 — Iterate"/>

Three structured experiments:

<details>
  <summary><b>Exp. 1 — Improve a specialist prompt</b></summary>
  <br/>

Open `src/agents/specialists/data.py`. Compare its `DATA_SYSTEM_PROMPT` to
`platform.py`. The data prompt names specific services; the platform prompt
is more generic. Edit the platform prompt to mention concrete services and
runbooks, then run `make tui api-gateway` to see whether the response
becomes more concrete.

</details>

<details>
  <summary><b>Exp. 2 — Try different incidents</b></summary>
  <br/>

```bash
make tui api-gateway          # platform tier-1 — large cascade
make tui k8s-controller       # infra — cross-department
make tui experiment-tracker   # ml tier-3 — small blast radius
make tui postgres-primary     # data — large cascade through product
```

For each: predict which specialist gets called, how many services are
in the blast radius, and which departments. Verify in the TUI.

</details>

<details>
  <summary><b>Exp. 3 — Add a service to the topology</b></summary>
  <br/>

Append to `src/infrastructure/topology.py`:

```python
Service(
    name="audit-log",
    department=Department.PLATFORM,
    description="Immutable audit log for compliance",
    tier=2,
    region="us-east-1",
    depends_on=["kafka-broker", "postgres-primary"],
    sla_minutes=26.28,
    tags=["audit", "compliance"],
    metadata={"port": 8095, "owners": ["platform-team"]},
)
```

Re-seed (`make seed`), then run `make tui audit-log`. The blast radius of
`kafka-broker` now includes `audit-log` automatically — the graph query
discovered it without any agent code changing.

</details>

<br/>

<a id="b7-endgame"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,6,11&height=56&section=header&text=B7%20%E2%80%94%20Endgame%20challenges&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20choose-your-own%20advanced%20extensions&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B7 — Endgame"/>

Four optional extensions if you finished early. Pick one — they're each
substantial enough to fill the time.

<details>
  <summary><b>1. Reflect and re-retrieve</b></summary>

After the specialist analysis, add a reflection step that scores the
analysis's confidence and re-runs the vector search with a more specific
query if confidence is low.

</details>

<details>
  <summary><b>2. Cross-department fan-out</b></summary>

When the router flags `CROSS-DEPARTMENT`, dispatch all affected
specialists in parallel. See [`langgraph.graph.Send`](https://langchain-ai.github.io/langgraph/concepts/low_level/#send).

</details>

<details>
  <summary><b>3. Memory across incidents</b></summary>

Write the specialist analysis back into Qdrant tagged with the service.
On the next incident for the same service, triage retrieves it as prior
context. Does the response improve? Does recall@k change?

</details>

<details>
  <summary><b>4. Replace Cypher with LLM reasoning</b></summary>

Comment out `_cypher_blast_radius()` and replace it with an LLM that
reasons about cascades from vector context alone. Compare accuracy
against the Cypher ground truth using `make eval`.

</details>

<br/>

---

# 🏁 Recap — the one-line answer

<div align="center">

<table>
  <tr>
    <td align="center" width="33%">
      <b>Plain RAG</b><br/>
      <sub>retrieves <b>facts</b></sub>
    </td>
    <td align="center" width="33%">
      <b>Graph RAG</b><br/>
      <sub>retrieves facts <b>+ relationships</b></sub>
    </td>
    <td align="center" width="33%">
      <b>Agentic RAG</b><br/>
      <sub>decides <b>what · from where · who acts</b></sub>
    </td>
  </tr>
</table>

</div>

<br/>

<div align="center">

### You made it!

If this clicked for you, **drop a star on the repo** and share what you built.

<br/>

<a href="README.md"><img src="https://img.shields.io/badge/⬅%20Back%20to%20README-8B5CF6?style=for-the-badge&labelColor=0f0f1e" alt="Back to README"/></a>
<a href="workshop-game.html"><img src="https://img.shields.io/badge/🎮%20Track%20your%20progress-06B6D4?style=for-the-badge&labelColor=0f0f1e" alt="Game"/></a>
<a href="https://github.com/martin76ec/agentic-rag-workshop/stargazers"><img src="https://img.shields.io/badge/⭐%20Star%20the%20repo-EC4899?style=for-the-badge&labelColor=0f0f1e" alt="Star"/></a>

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,6&height=120&section=footer&animation=fadeIn" alt="footer banner" width="100%"/>

<sub>Workshop v2.0.0 · two tracks · seven parts · <a href="#briefing">Top</a></sub>

</div>
