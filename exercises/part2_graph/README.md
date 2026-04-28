# Parte 2 — Graph RAG: está roto, arréglalo

**Tiempo:** ~60 min
**Concepto:** Cypher · variable-length paths · fusión vector + grafo

## El problema

Plain RAG quedó arreglado pero sigue sin nombrar la cascada. Cuando Kafka cae,
la respuesta dice "podría afectar otros servicios" en lugar de listar los 5
servicios concretos que se rompen con él.

La razón: nunca consultamos el grafo. La topología vive en Neo4j pero el
pipeline solo consulta Qdrant. Tu trabajo: agregar dos consultas Cypher y
fusionar el resultado con el contexto vectorial.

## Las tres fallas

| # | Archivo | Síntoma observable |
|---|---|---|
| 2.1 | `neighborhood.cypher` | Devuelve un servicio sin sus dependencias ni quién depende de él. |
| 2.2 | `blast_radius.py` | Solo descubre dependientes directos. La cascada `kafka → clickhouse → tracker` no se ve. |
| 2.3 | `fusion.py` | El contexto del grafo se concatena al final como un muro de texto. El LLM lo ignora. |

## Cómo trabajarlas

```bash
make exercise 2.1
make check 2.1
```

## Cuándo pasar a la Parte 3

Cuando los tres tests verdes y la consulta `MATCH path = (a)-[:DEPENDS_ON*1..4]->(b {name: 'kafka-broker'}) RETURN path` en Neo4j browser muestre la cascada como un árbol.
