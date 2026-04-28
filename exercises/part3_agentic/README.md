# Parte 3 — Agentic RAG: está roto, arréglalo

**Tiempo:** ~75 min
**Concepto:** triage classifier · enrutamiento · estado compartido · prompt por especialista

## El problema

Plain RAG y Graph RAG ya devuelven contexto preciso, pero todavía aplican el
mismo system prompt a cualquier incidente. Una caída de Kafka y una de
Postgres reciben el mismo razonamiento genérico. La fase agéntica resuelve
esto: triage clasifica, router decide, especialista ejecuta.

Sólo que… el triage clasifica todo como "platform", el router ignora el
blast radius, el estado no propaga, y el especialista usa un prompt genérico.
Cuatro fallas para arreglar.

## Las cuatro fallas

| # | Archivo | Síntoma observable |
|---|---|---|
| 3.1 | `triage.py` | El clasificador siempre devuelve "platform" porque el JSON del LLM se parsea mal y cae al fallback. |
| 3.2 | `router.py` | El router elige el especialista por regex sobre el nombre del servicio, ignorando `blast_radius_report.affected_departments`. |
| 3.3 | `state.py` | Faltan campos del estado: `blast_radius_report`, `triage_classification`. El especialista recibe contexto vacío. |
| 3.4 | `specialists/data.py` | El system prompt es el mismo "you are a specialist" para todos los departamentos. Ningún experto. |

## Cómo trabajarlas

```bash
make exercise 3.1
make check 3.1
```

## Cuándo terminar

Cuando los cuatro tests pasen y `make tui kafka-broker` muestre output con
los runbooks específicos de Kafka que vienen del prompt experto.
