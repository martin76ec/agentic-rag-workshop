<!-- ════════════════════════════════════════════════════════════════════════ -->
<!--                          ✦   HEADER BANNER   ✦                          -->
<!-- ════════════════════════════════════════════════════════════════════════ -->

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,6&height=240&section=header&text=El%20Taller&fontSize=64&fontColor=ffffff&fontAlignY=38&desc=Construye%20un%20RAG.%20Despu%C3%A9s%20aprende%20cu%C3%A1ndo%20doblarlo.&descAlignY=62&descSize=16&animation=fadeIn" alt="Workshop banner" width="100%"/>

<br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=2800&pause=900&color=06B6D4&center=true&vCenter=true&width=720&lines=Dos+v%C3%ADas.+Mismo+incidente.;V%C3%ADa+A+%E2%86%92+construye+un+RAG+desde+c%C3%B3digo+roto.;V%C3%ADa+B+%E2%86%92+compara+arquitecturas+y+m%C3%ADdelas.;Ej%C3%A9cutalo+%E2%86%92+obs%C3%A9rvalo+%E2%86%92+r%C3%B3mpelo+%E2%86%92+rec%C3%B3nstruyelo." alt="Typing tagline"/>

<br/><br/>

<img src="https://img.shields.io/badge/⏱%20duraci%C3%B3n-~6%20horas-8B5CF6?style=for-the-badge&labelColor=0f0f1e" alt="duración"/>
<img src="https://img.shields.io/badge/📚%20partes-7-06B6D4?style=for-the-badge&labelColor=0f0f1e" alt="partes"/>
<img src="https://img.shields.io/badge/🧠%20nivel-principiante→intermedio-EC4899?style=for-the-badge&labelColor=0f0f1e" alt="nivel"/>
<img src="https://img.shields.io/badge/🛠%20prereq-make%20setup%20%26%26%20make%20seed-F43F5E?style=for-the-badge&labelColor=0f0f1e" alt="prereqs"/>

<br/>

<a href="WORKSHOP.md"><img src="https://img.shields.io/badge/🇬🇧%20Read%20in%20English-1a1a2e?style=for-the-badge&labelColor=0f0f1e" alt="Read in English"/></a>

<br/><br/>

[🎬&nbsp;Briefing](#briefing) &nbsp;•&nbsp;
[A1&nbsp;Plain](#a1-plain) &nbsp;•&nbsp;
[A2&nbsp;Graph](#a2-graph) &nbsp;•&nbsp;
[A3&nbsp;Agentic](#a3-agentic) &nbsp;•&nbsp;
[B4&nbsp;Comparar](#b4-comparar) &nbsp;•&nbsp;
[B5&nbsp;Medir](#b5-medir) &nbsp;•&nbsp;
[B6&nbsp;Iterar](#b6-iterar) &nbsp;•&nbsp;
[B7&nbsp;Endgame](#b7-endgame)

</div>

<br/>

<a id="briefing"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,16,6&height=56&section=header&text=Briefing&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=Un%20incidente%20de%20guardia%20te%20cae%20encima%20a%20las%203am&descAlignY=68&descSize=13&descColor=e2e2e2" alt="Briefing"/>

<div align="center">

<table>
  <tr>
    <td align="center" width="120">
      <img src="https://img.icons8.com/fluency/72/error.png" width="56" alt=""/>
    </td>
    <td>
      <b>📟 PagerDuty acaba de despertarte.</b><br/>
      <code>kafka-broker</code> está devolviendo errores 5xx. El consumer lag crece.<br/>
      Los servicios fallan al conectar. <b>Son las 3 AM. Estás de guardia.</b>
    </td>
  </tr>
</table>

</div>

Tu trabajo: averiguar **qué se rompió**, **qué más está en riesgo** y **qué
hacer al respecto** — y, en el camino, construir el RAG que te ayuda a
hacerlo.

Este taller tiene dos vías que comparten el mismo escenario:

| Vía | Qué haces | Para quién | Tiempo |
|:--|:--|:--|:--|
| **A — Construirlo** | Arreglas tres implementaciones de RAG deliberadamente rotas. Cada parte trae código que corre pero da malas respuestas. Diagnosticas, arreglas los TODO y observas cómo mejoran las métricas. | Principiantes en RAG | ~3 h |
| **B — Compararlo** | Ejecutas la implementación de referencia en tres modos. Mides la calidad de retrieval. Iteras prompts y topología. | Intermedios | ~3 h |

> [!IMPORTANT]
> **Lleva esta pregunta contigo durante todo el taller:**
> *¿Qué sabe el sistema ahora que no sabía en el paso anterior — y cómo cambia eso la respuesta?*

<br/>

---

# 🛠️ Vía A — Construirlo

Empiezas con un RAG que "más o menos funciona". Cada parte identifica una
falla distinta y la arreglas. Los archivos viven en
`exercises/part1_plain/`, `exercises/part2_graph/` y `exercises/part3_agentic/`.

```bash
make exercise 1.1     # muestra el output roto y corre los tests
make verify   1.1     # solo los tests
make solution 1.1     # te dice qué archivo en src/ es la referencia
```

<br/>

<a id="a1-plain"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=11,6,20&height=56&section=header&text=A1%20%E2%80%94%20Plain%20RAG%20(est%C3%A1%20roto%2C%20arr%C3%A9glalo)&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20chunking%20%C2%B7%20top-k%20%C2%B7%20construcci%C3%B3n%20del%20prompt&descAlignY=68&descSize=13&descColor=e2e2e2" alt="A1 — Plain RAG"/>

<img src="https://img.shields.io/badge/ejercicios-3-06B6D4?style=flat-square&labelColor=0f0f1e"/>
<img src="https://img.shields.io/badge/conceptos-chunking%20%C2%B7%20top--k%20%C2%B7%20prompt-06B6D4?style=flat-square&labelColor=0f0f1e"/>

El starter trae un Plain RAG con tres problemas en los que cae cualquier RAG
nuevo. Vas a sentir cada uno en la salida del LLM antes de arreglarlo.

| # | Qué está roto | Qué vas a aprender |
|:--|:--|:--|
| **1.1** | Cada servicio es un solo chunk gigante. La búsqueda devuelve el servicio correcto para cualquier query, pero el embedding no diferencia "qué hace Kafka" de "qué depende de Kafka". | Por qué importa el chunking sectionado; cómo la forma del chunk cambia el recall. |
| **1.2** | `top_k=1` y sin filtros por metadatos. Las entradas de "department knowledge" se filtran como si fueran servicios. | Cómo ajustar k; usar `filters` para acotar; filtrado por campo. |
| **1.3** | El system prompt menciona "context" pero nunca inserta los chunks recuperados en el mensaje. El LLM se queda sin grounding. | Construcción del prompt; bloques de contexto estructurados. |

<details>
  <summary><b>Cómo correr cada arreglo</b></summary>
  <br/>

```bash
# 1.1 — Chunking
make exercise 1.1
# Edita exercises/part1_plain/chunking.py, arregla los TODO.
make verify 1.1

# 1.2 — Top-k y filtrado
make exercise 1.2
# Edita exercises/part1_plain/search.py.
make verify 1.2

# 1.3 — Construcción del prompt
make exercise 1.3
# Edita exercises/part1_plain/prompt.py.
make verify 1.3
```

Pistas progresivas: `exercises/part1_plain/hints.md`. Léelas de a una.

</details>

> [!TIP]
> Antes de tocar 1.1, mira qué devuelve `chunk_service()` y pregúntate: ¿qué
> consultas NUNCA matchearían el hit correcto? Eso te dice por dónde cortar.

<br/>

<a id="a2-graph"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=6,11,20&height=56&section=header&text=A2%20%E2%80%94%20Graph%20RAG%20(est%C3%A1%20roto%2C%20arr%C3%A9glalo)&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=60%20min%20%E2%80%94%20Cypher%20%C2%B7%20variable-length%20paths%20%C2%B7%20fusi%C3%B3n&descAlignY=68&descSize=13&descColor=e2e2e2" alt="A2 — Graph RAG"/>

<img src="https://img.shields.io/badge/ejercicios-3-8B5CF6?style=flat-square&labelColor=0f0f1e"/>
<img src="https://img.shields.io/badge/conceptos-Cypher%20%C2%B7%20paths%20%C2%B7%20fusi%C3%B3n-8B5CF6?style=flat-square&labelColor=0f0f1e"/>

Plain RAG quedó arreglado, pero el LLM sigue diciendo *"podría afectar
servicios downstream"* en términos vagos. La cascada vive en Neo4j — solo
que nunca la consultaste.

| # | Qué está roto | Qué vas a aprender |
|:--|:--|:--|
| **2.1** | El query de vecindario devuelve las propiedades del servicio pero no sus dependencias. | Cypher MATCH/OPTIONAL MATCH; `collect(DISTINCT ...)`. |
| **2.2** | El query de blast radius solo encuentra dependientes directos. Las cascadas tipo `kafka → clickhouse → tracker` son invisibles. | Variable-length paths `*1..N`; binding a `path` y devolver nodos. |
| **2.3** | El contexto vectorial y el del grafo se concatenan como un muro de texto. El LLM ignora el grafo porque queda al final y sin estructura. | Fusión por prioridad; secciones estructuradas en el prompt. |

<details>
  <summary><b>Verifica la cascada en Neo4j browser</b></summary>
  <br/>

```cypher
MATCH path = (aff:Service)-[:DEPENDS_ON*1..4]->(root:Service {name: 'kafka-broker'})
RETURN path
```

Deberías ver Kafka en el centro con cadenas radiando hacia afuera.

</details>

<br/>

<a id="a3-agentic"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,6,11&height=56&section=header&text=A3%20%E2%80%94%20Agentic%20RAG%20(est%C3%A1%20roto%2C%20arr%C3%A9glalo)&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=75%20min%20%E2%80%94%20triage%20%C2%B7%20router%20%C2%B7%20estado%20%C2%B7%20especialista&descAlignY=68&descSize=13&descColor=e2e2e2" alt="A3 — Agentic RAG"/>

<img src="https://img.shields.io/badge/ejercicios-4-EC4899?style=flat-square&labelColor=0f0f1e"/>
<img src="https://img.shields.io/badge/conceptos-classifier%20%C2%B7%20routing%20%C2%B7%20estado%20%C2%B7%20expertise-EC4899?style=flat-square&labelColor=0f0f1e"/>

Plain + Graph ya dan contexto preciso, pero el LLM sigue aplicando el mismo
prompt genérico a cualquier incidente. La fase agéntica resuelve eso —
clasifica, enruta y ejecuta un especialista con conocimiento del dominio.

| # | Qué está roto | Qué vas a aprender |
|:--|:--|:--|
| **3.1** | El triage clasifica todo como `platform` porque el JSON del LLM viene envuelto en backticks de markdown y el parser no tolera eso. | Parseo defensivo de JSON; coerción a enums. |
| **3.2** | El router elige especialista por regex sobre el nombre del servicio, ignorando el blast-radius report. Los incidentes cross-departamento son silenciosos. | Leer estado en LangGraph; marcar blast multi-equipo. |
| **3.3** | El TypedDict del estado solo carga `messages`. Los especialistas reciben contexto vacío. | Diseño del estado del agente; qué lee y escribe cada nodo. |
| **3.4** | El system prompt del especialista de data es genérico — el mismo que el de platform. Ningún experto se filtra. | System prompts por rol; lenguaje operativo concreto. |

> [!NOTE]
> **El momento "agéntico".** Cuando 3.1–3.3 están en verde, la decisión del
> router se basa en `blast_radius_report.affected_departments`, que el agente
> de triage recuperó de Neo4j. **El retrieval informa al routing, que
> determina qué se recupera después.** Ese loop de retroalimentación es lo
> que hace al sistema "agéntico" en lugar de un pipeline estático.

<br/>

> [!TIP]
> **Toma un descanso de 20 min.** La Vía B requiere mucho menos tipeo —
> perfecta para después del café.

<br/>

---

# 📊 Vía B — Compararlo

La Vía A construyó un RAG funcional. La Vía B lo compara contra la
implementación de referencia en `src/`, mide la calidad de retrieval con
un gold set e itera prompts y topología.

```bash
make rag       kafka-broker     # Plain RAG (solo vector)
make graph-rag kafka-broker     # Graph RAG (+ Neo4j)
make tui       kafka-broker     # Agentic RAG (pipeline completo)
make eval                       # Métricas de retrieval
```

<br/>

<a id="b4-comparar"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=11,6,20&height=56&section=header&text=B4%20%E2%80%94%20Tres%20modos%20lado%20a%20lado&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=30%20min%20%E2%80%94%20mismo%20incidente%2C%20tres%20arquitecturas&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B4 — Comparar"/>

Corre el mismo incidente por los tres modos en pestañas separadas:

```bash
make rag kafka-broker        # 🔵 Plain
make graph-rag kafka-broker  # 🟣 Graph
make tui kafka-broker        # 🌈 Agentic
```

<div align="center">

| Pregunta | Plain | Graph | Agentic |
|:--|:--:|:--:|:--:|
| ¿Qué servicios están en riesgo? | Vago | Exacto (5 nombrados) | Exacto + departamentos |
| ¿A quién paginar? | Genérico | Genérico | `data-oncall` específicamente |
| ¿Qué comando Kafka correr? | Improbable | Improbable | Probable (el especialista sabe) |
| Llamadas LLM | `1` | `1` | `2` |
| Pasos de retrieval | `1` | `3` | `4–5` |

</div>

<br/>

<a id="b5-medir"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=6,11,20&height=56&section=header&text=B5%20%E2%80%94%20Medir%20la%20calidad%20de%20retrieval&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20gold%20set%2C%20recall%40k%2C%20precision%40k%2C%20MRR&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B5 — Medir"/>

Las comparaciones de arquitectura son subjetivas hasta que tienes métricas.
El harness en `eval/` corre un gold set de 15 queries contra cualquier
retriever y calcula:

- **Recall@k** — fracción de servicios esperados que aparecen en top-k
- **Precision@k** — fracción de top-k que estaban en los esperados
- **MRR** (Mean Reciprocal Rank) — premia rankear primero el correcto

```bash
make eval                              # default: modo vector, k=5
make eval MODE=graph                   # vector + Neo4j
make eval MODE=graph K=10              # top-k más amplio
```

<details>
  <summary><b>Lee el gold set</b></summary>
  <br/>

`eval/gold_set.json` tiene 15 pares `(query, expected_services)` que cubren
los 5 departamentos. Cada query es del tipo que un on-call tipearía a las
3 AM. Agrega los tuyos — es solo JSON.

</details>

> [!TIP]
> Corre `make eval` *antes* y *después* de implementar el ejercicio 1.2 de
> la Vía A (top-k + filtros). El salto en recall es la evidencia más directa
> de que el arreglo importa.

<br/>

<a id="b6-iterar"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,16,6&height=56&section=header&text=B6%20%E2%80%94%20Iterar%20prompts%20y%20topolog%C3%ADa&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20rompe%20cosas%20a%20prop%C3%B3sito%20y%20mira%20qu%C3%A9%20cede&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B6 — Iterar"/>

Tres experimentos estructurados:

<details>
  <summary><b>Exp. 1 — Mejora un prompt de especialista</b></summary>
  <br/>

Abre `src/agents/specialists/data.py`. Compara su `DATA_SYSTEM_PROMPT` con
el de `platform.py`. El prompt de data nombra servicios específicos; el de
platform es más genérico. Edita el de platform para que mencione servicios
y runbooks concretos, y luego corre `make tui api-gateway` para ver si la
respuesta se vuelve más concreta.

</details>

<details>
  <summary><b>Exp. 2 — Prueba distintos incidentes</b></summary>
  <br/>

```bash
make tui api-gateway          # platform tier-1 — cascada grande
make tui k8s-controller       # infra — cross-departamento
make tui experiment-tracker   # ml tier-3 — blast radius pequeño
make tui postgres-primary     # data — gran cascada vía product
```

Para cada uno: predice qué especialista se llama, cuántos servicios hay
en el blast radius, y qué departamentos. Verifica en el TUI.

</details>

<details>
  <summary><b>Exp. 3 — Agrega un servicio a la topología</b></summary>
  <br/>

Agrega a `src/infrastructure/topology.py`:

```python
Service(
    name="audit-log",
    department=Department.PLATFORM,
    description="Log de auditoría inmutable para compliance",
    tier=2,
    region="us-east-1",
    depends_on=["kafka-broker", "postgres-primary"],
    sla_minutes=26.28,
    tags=["audit", "compliance"],
    metadata={"port": 8095, "owners": ["platform-team"]},
)
```

Re-siembra (`make seed`) y corre `make tui audit-log`. El blast radius de
`kafka-broker` ahora incluye `audit-log` automáticamente — el query de
grafo lo descubrió sin que tocaras código de agentes.

</details>

<br/>

<a id="b7-endgame"></a>
<img width="100%" src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=20,6,11&height=56&section=header&text=B7%20%E2%80%94%20Desaf%C3%ADos%20endgame&fontColor=ffffff&fontSize=22&fontAlignY=36&desc=45%20min%20%E2%80%94%20extensiones%20avanzadas%20a%20elecci%C3%B3n&descAlignY=68&descSize=13&descColor=e2e2e2" alt="B7 — Endgame"/>

Cuatro extensiones opcionales si terminaste antes. Elige una — cada una
tiene tamaño suficiente para llenar el tiempo.

<details>
  <summary><b>1. Reflexionar y volver a recuperar</b></summary>

Después del análisis del especialista, agrega un paso de reflexión que
puntúe la confianza y vuelva a correr la búsqueda vectorial con un query
más específico si la confianza es baja.

</details>

<details>
  <summary><b>2. Fan-out cross-departamento</b></summary>

Cuando el router marca `CROSS-DEPARTMENT`, despacha en paralelo a todos
los especialistas afectados. Mira [`langgraph.graph.Send`](https://langchain-ai.github.io/langgraph/concepts/low_level/#send).

</details>

<details>
  <summary><b>3. Memoria entre incidentes</b></summary>

Escribe el análisis del especialista en Qdrant etiquetado por servicio.
En el siguiente incidente del mismo servicio, el triage lo recupera como
contexto previo. ¿Mejora la respuesta? ¿Cambia el recall@k?

</details>

<details>
  <summary><b>4. Reemplaza Cypher por razonamiento del LLM</b></summary>

Comenta `_cypher_blast_radius()` y reemplázalo por un LLM que razone sobre
cascadas a partir solo del contexto vectorial. Compara la precisión contra
el ground truth de Cypher usando `make eval`.

</details>

<br/>

---

# 🏁 Resumen — la respuesta en una línea

<div align="center">

<table>
  <tr>
    <td align="center" width="33%">
      <b>Plain RAG</b><br/>
      <sub>recupera <b>hechos</b></sub>
    </td>
    <td align="center" width="33%">
      <b>Graph RAG</b><br/>
      <sub>recupera hechos <b>+ relaciones</b></sub>
    </td>
    <td align="center" width="33%">
      <b>Agentic RAG</b><br/>
      <sub>decide <b>qué · de dónde · quién actúa</b></sub>
    </td>
  </tr>
</table>

</div>

<br/>

<div align="center">

### ¡Lo lograste!

Si esto te hizo clic, **deja una estrella en el repo** y comparte lo que construiste.

<br/>

<a href="README.md"><img src="https://img.shields.io/badge/⬅%20Volver%20al%20README-8B5CF6?style=for-the-badge&labelColor=0f0f1e" alt="Volver al README"/></a>
<a href="workshop-game.html"><img src="https://img.shields.io/badge/🎮%20Sigue%20tu%20progreso-06B6D4?style=for-the-badge&labelColor=0f0f1e" alt="Game"/></a>
<a href="https://github.com/martin76ec/agentic-rag-workshop/stargazers"><img src="https://img.shields.io/badge/⭐%20Estrella%20el%20repo-EC4899?style=for-the-badge&labelColor=0f0f1e" alt="Star"/></a>

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,6&height=120&section=footer&animation=fadeIn" alt="footer banner" width="100%"/>

<sub>Workshop v2.0.0 · dos vías · siete partes · <a href="#briefing">Top</a></sub>

</div>
