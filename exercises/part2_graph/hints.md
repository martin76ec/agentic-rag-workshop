# Pistas — Parte 2 (Graph RAG)

---

## 2.1 — neighborhood.cypher

<details>
<summary>Pista 1: forma del query</summary>

```cypher
MATCH (s:Service {name: $service})
OPTIONAL MATCH (s)-[:DEPENDS_ON]->(dep:Service)
OPTIONAL MATCH (aff:Service)-[:DEPENDS_ON]->(s)
RETURN s.tier   AS tier,
       s.department AS dept,
       collect(DISTINCT dep.name) AS depends_on,
       collect(DISTINCT aff.name) AS depended_by
```

</details>

<details>
<summary>Pista 2: por qué OPTIONAL MATCH</summary>

`OPTIONAL` permite que el query devuelva una fila aunque no haya
dependencias en alguna dirección. Sin `OPTIONAL`, un servicio sin
dependientes no devolvería nada.

</details>

---

## 2.2 — blast_radius.py

<details>
<summary>Pista 1: variable-length path</summary>

```cypher
MATCH path = (aff:Service)-[:DEPENDS_ON*1..4]->(root:Service {name: $service})
RETURN aff.name AS name,
       aff.department AS dept,
       [n IN nodes(path) | n.name] AS path_nodes
```

</details>

<details>
<summary>Pista 2: parameterizar max_hops</summary>

```python
BLAST_TEMPLATE = """
MATCH path = (aff:Service)-[:DEPENDS_ON*1..{hops}]->(root:Service {{name: $service}})
RETURN aff.name AS name,
       aff.department AS dept,
       [n IN nodes(path) | n.name] AS path_nodes
"""

def blast_radius_cypher(max_hops: int = 4) -> str:
    return BLAST_TEMPLATE.format(hops=max_hops)
```

Atención al doble `{{name: $service}}` — la primera llave escapa la
interpolación de Python para que Cypher reciba `{name: $service}`.

</details>

---

## 2.3 — fusion.py

<details>
<summary>Pista 1: secciones</summary>

```python
def render_topology(n):
    return (
        "### Topology (Neo4j)\n"
        f"- Tier: {n['tier']}\n"
        f"- Department: {n['department']}\n"
        f"- Depends on: {', '.join(n['depends_on']) or 'none'}\n"
        f"- Depended on by: {', '.join(n['depended_by']) or 'none'}\n"
    )

def render_cascade(paths):
    chains = [' → '.join(p) for p in paths[:5]]
    body = '\n'.join(f"- {c}" for c in chains)
    return f"### Cascade paths\n{body}\n"

def render_supporting(hits):
    body = '\n'.join(
        f"- {h['metadata']['service_name']}: {h['memory']}"
        for h in hits
    )
    return f"### Supporting context (Qdrant)\n{body}\n"
```

</details>

<details>
<summary>Pista 2: ensamblado final</summary>

```python
return (
    f"{render_topology(neighborhood)}\n"
    f"{render_cascade(blast_paths)}\n"
    f"{render_supporting(vector_hits)}\n"
    f"## Question\n{query}\n"
)
```

</details>
