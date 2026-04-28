import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable


class EventKind(Enum):
    NODE_START = auto()
    NODE_DONE = auto()
    VECTOR_SEARCH_START = auto()
    VECTOR_SEARCH_DONE = auto()
    GRAPH_BFS_START = auto()
    GRAPH_BFS_DONE = auto()
    LLM_START = auto()
    LLM_DONE = auto()
    ROUTING = auto()
    PIPELINE_DONE = auto()


@dataclass
class Event:
    kind: EventKind
    node: str
    data: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


_lock = threading.Lock()
_handler: Callable[[Event], None] | None = None


def register_handler(fn: Callable[[Event], None]) -> None:
    global _handler
    with _lock:
        _handler = fn


def clear_handler() -> None:
    global _handler
    with _lock:
        _handler = None


def emit(event: Event) -> None:
    with _lock:
        h = _handler
    if h is not None:
        try:
            h(event)
        except Exception:
            pass
