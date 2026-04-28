import threading

_local = threading.local()


def set_current_node(name: str) -> None:
    _local.node = name


def get_current_node() -> str:
    return getattr(_local, "node", "unknown")
