from src.agents.specialists import get_specialist
from src.agents.state import TriageState
from src.infrastructure.models import Department


def specialist_node(state: TriageState) -> dict:
    department = state.get("department", Department.INFRA)
    specialist_fn = get_specialist(department)
    return specialist_fn(state)
