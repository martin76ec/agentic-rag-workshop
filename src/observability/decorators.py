import os

import agentops

_agentops_initialized = False


def init_agentops() -> None:
    global _agentops_initialized
    if _agentops_initialized:
        return

    api_key = os.getenv("AGENTOPS_API_KEY")
    if not api_key:
        return

    api_host = os.getenv("AGENTOPS_API_HOST")
    kwargs = {
        "api_key": api_key,
        "auto_start_session": False,
        "tags": ["triage-agent", "infrastructure"],
    }
    if api_host:
        kwargs["api_host"] = api_host

    agentops.init(**kwargs)
    _agentops_initialized = True


def begin_session():
    """Start an AgentOps session. Returns None if AgentOps is not configured."""
    if not _agentops_initialized:
        return None
    return agentops.start_session(tags=["triage-agent", "infrastructure"])


def end_session(session, *, success: bool = True) -> None:
    if session is None:
        return
    session.end_session(end_state="Success" if success else "Fail")


def record_node_event(node_name: str, state_delta: dict, elapsed: float) -> None:
    if not _agentops_initialized:
        return
    try:
        from agentops import ActionEvent  # noqa: PLC0415
        safe_delta = {
            k: str(v)[:500]
            for k, v in state_delta.items()
            if k not in ("messages", "incident", "blast_radius_report") and v
        }
        agentops.record(ActionEvent(
            action_type=f"node:{node_name}",
            params={"node": node_name, "elapsed_s": round(elapsed, 2)},
            returns=safe_delta,
        ))
    except Exception:
        pass
