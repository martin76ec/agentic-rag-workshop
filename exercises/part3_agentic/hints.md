# Pistas — Parte 3 (Agentic RAG)

---

## 3.1 — Triage classifier

<details>
<summary>Pista 1: strip de markdown</summary>

```python
cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", llm_response.strip())
```

</details>

<details>
<summary>Pista 2: extracción del primer JSON balanceado</summary>

```python
match = re.search(r"\{.*\}", cleaned, re.DOTALL)
json_text = match.group(0) if match else cleaned
```

</details>

<details>
<summary>Pista 3: validación de enums sin pisar valores correctos</summary>

```python
sev_str = data.get("severity_classification", "").lower()
try:
    severity = Severity(sev_str)
except ValueError:
    severity = Severity.MEDIUM

dept_str = data.get("department", "").lower()
try:
    department = Department(dept_str)
except ValueError:
    department = Department.PLATFORM
```

</details>

---

## 3.2 — Router

<details>
<summary>Pista 1: forma del retorno</summary>

```python
target = triage_department
cross = False
if blast_radius_report and len(set(blast_radius_report.affected_departments)) > 1:
    cross = True

rationale = (
    f"Routing to {target.value} specialist"
    + (f" — CROSS-DEPARTMENT impact across {len(blast_radius_report.affected_departments)} teams"
       if cross else "")
)
```

</details>

---

## 3.3 — State

<details>
<summary>Pista 1: campos completos</summary>

```python
from src.infrastructure.models import BlastRadiusReport, Department, Incident

class TriageState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    incident: Incident | None
    service_name: str
    department: Department | None
    blast_radius_report: BlastRadiusReport | None
    triage_classification: str
    routing_decision: str
    specialist_analysis: str
    final_report: str
```

</details>

---

## 3.4 — Data specialist

<details>
<summary>Pista 1: estructura del system prompt</summary>

```python
DATA_SYSTEM_PROMPT = (
    "You are the Data department specialist. You own and operate:\n"
    "  - postgres-primary  (replication, failover, connection pooling)\n"
    "  - redis-cache       (eviction policies, cluster sharding)\n"
    "  - kafka-broker      (partition rebalancing, consumer-group lag)\n"
    "  - clickhouse-analytics (schema design, merge tree, query plans)\n\n"
    "When given an incident, respond with:\n"
    "  1. Root cause hypothesis\n"
    "  2. Immediate mitigation steps (concrete commands)\n"
    "  3. Long-term remediation\n"
    "  4. Impact on data services downstream"
)
```

</details>

<details>
<summary>Pista 2: user prompt assembly</summary>

```python
def build_specialist_prompt(triage_summary, blast_summary, vector_context):
    return (
        f"## Triage\n{triage_summary}\n\n"
        f"## Blast radius\n{blast_summary}\n\n"
        f"## Retrieved context\n{vector_context}\n\n"
        "Provide root cause, mitigation, remediation, and impact assessment."
    )
```

</details>
