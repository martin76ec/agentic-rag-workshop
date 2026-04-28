# Pistas — Parte 1 (Plain RAG)

> Lee una pista a la vez. Si te quedas trabado, sigue a la siguiente.

---

## 1.1 — Chunking

<details>
<summary>Pista 1: ¿Qué busca el on-call?</summary>

Listas de preguntas que la búsqueda vectorial debería responder bien:
- "¿qué hace kafka-broker?" → identidad
- "¿qué depende de kafka-broker?" → dependientes
- "¿quién es dueño de kafka-broker?" → departamento
- "SLA de kafka-broker" → operaciones

Cada una es un chunk distinto.

</details>

<details>
<summary>Pista 2: Plantilla sugerida</summary>

```python
return [
    f"{service.name}: {service.description}",
    f"{service.name} owner: {service.department.value} team, tier {service.tier}.",
    f"{service.name} depends on: {', '.join(service.depends_on) or 'none'}.",
    f"{service.name} SLA: {service.sla_minutes} minutes per month. Tags: {', '.join(service.tags) or 'none'}.",
]
```

</details>

<details>
<summary>Pista 3: Solución de referencia</summary>

`src/memory/graph.py::service_to_memory_content` produce un único chunk
porque el sistema de referencia delega chunking a Mem0. Tu versión
sectionada es deliberadamente más educativa.

</details>

---

## 1.2 — Search

<details>
<summary>Pista 1: top_k</summary>

5 es un buen default para triage. Tres es el mínimo razonable para que
los tests pasen.

</details>

<details>
<summary>Pista 2: filtros</summary>

```python
results = memory.search(
    query,
    filters={"user_id": "infrastructure"},
    top_k=top_k,
)
hits = [
    r for r in results.get("results", [])
    if r.get("metadata", {}).get("type") == "service"
]
```

</details>

<details>
<summary>Pista 3: filtro por departamento</summary>

```python
if department:
    hits = [h for h in hits if h["metadata"].get("department") == department]
```

</details>

---

## 1.3 — Prompt

<details>
<summary>Pista 1: cómo renderizar un hit</summary>

```python
def render(h):
    md = h.get("metadata", {})
    return f"- {md.get('service_name', '?')} ({md.get('department', '?')}, tier {md.get('tier', '?')}): {h.get('memory', '')}"
```

</details>

<details>
<summary>Pista 2: armado del prompt</summary>

```python
context_block = "\n".join(render(h) for h in hits) or "(no results)"
prompt = (
    f"## Context retrieved from infrastructure memory\n{context_block}\n\n"
    f"## Question\n{query}\n\n"
    "Answer concretely. Name services. Cite the cascade path."
)
```

</details>
