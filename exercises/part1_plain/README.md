# Parte 1 — Plain RAG: está roto, arréglalo

**Tiempo:** ~45 min
**Concepto:** chunking · top-k · construcción del prompt

## El problema

Tienes un RAG básico que "más o menos funciona". El equipo de guardia se queja
de que las respuestas son vagas, no nombran servicios concretos y no ayudan a
las 3 AM. Tu trabajo: encontrar las tres fallas y arreglarlas una por una.

Cada fix se valida con un test que pasa cuando el comportamiento es correcto.

## Las tres fallas

| # | Archivo | Síntoma observable |
|---|---|---|
| 1.1 | `chunking.py` | Cada servicio es un solo chunk gigante. La búsqueda no separa hechos por sección. |
| 1.2 | `search.py` | Devuelve solo 1 resultado y no filtra por metadatos. Servicios de departamentos distintos se mezclan. |
| 1.3 | `prompt.py` | El system prompt menciona "context" pero nunca lo inserta en la consulta al LLM. |

## Cómo trabajarlas

```bash
make exercise 1.1     # corre el código roto, te muestra el output malo, luego corre los tests
make check 1.1        # solo los tests, sin el output ruidoso
make solution 1.1     # copia la solución de referencia (escape hatch si te trabaste)
```

Cada `*.py` tiene secciones marcadas `# TODO: ...` con el alcance exacto del
fix. Resiste la tentación de mirar `src/memory/graph.py` antes de intentarlo.

## Cuándo pasar a la Parte 2

Cuando los tres tests verdes:

```bash
make check 1.1 && make check 1.2 && make check 1.3
```
