from src.agents.specialists import get_specialist
from src.agents.state import TriageState
from src.infrastructure.models import Department
from src.tui.context import set_current_node
from src.tui.events import Event, EventKind, emit


def specialist_node(state: TriageState) -> dict:
    department = state.get("department", Department.INFRA)
    set_current_node("specialist")
    emit(Event(EventKind.NODE_START, "specialist", {"dept": department.value}))

    specialist_fn = get_specialist(department)
    result = specialist_fn(state)

    emit(Event(EventKind.NODE_DONE, "specialist", {
        "analysis": result.get("specialist_analysis", ""),
    }))
    return result
