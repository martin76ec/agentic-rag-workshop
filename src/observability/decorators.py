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


