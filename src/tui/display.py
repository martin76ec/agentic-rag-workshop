import threading
import time
from dataclasses import dataclass, field

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from src.tui.events import Event, EventKind

_SPINNER = "⣾⣽⣻⢿⡿⣟⣯⣷"
_SEV_COLORS = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "green",
    "info": "dim",
}
_NODE_COLORS = {"triage": "yellow", "router": "blue", "specialist": "green"}
_TOOL_COLORS = {"vector": "cyan", "graph": "magenta", "llm": "yellow"}


def _spin() -> str:
    return _SPINNER[int(time.time() * 10) % len(_SPINNER)]


@dataclass
class _ToolCall:
    kind: str        # "vector" | "graph" | "llm"
    title: str
    status: str = "running"
    lines: list[str] = field(default_factory=list)


@dataclass
class _Stage:
    name: str
    label: str
    status: str = "pending"  # "pending" | "running" | "done"
    elapsed: float = 0.0
    _start: float = 0.0
    tool_calls: list[_ToolCall] = field(default_factory=list)


_DEFAULT_STAGES = [
    ("triage", "Triage Agent"),
    ("router", "Router Agent"),
    ("specialist", "Specialist"),
]

_EXTRA_COLORS = {
    "rag": "cyan",
    "graph_rag": "magenta",
}


class TriageTUI:
    def __init__(self, incident, stages: list[tuple[str, str]] | None = None) -> None:
        self.incident = incident
        defs = stages if stages is not None else _DEFAULT_STAGES
        self.stages: list[_Stage] = [_Stage(name, label) for name, label in defs]
        self.analysis: str = ""
        self.routing: str = ""
        self._lock = threading.Lock()
        self._t0 = time.time()

    # ── Event handling ──────────────────────────────────────────────────

    def handle_event(self, event: Event) -> None:
        with self._lock:
            self._apply(event)

    def _get_stage(self, name: str) -> _Stage | None:
        return next((s for s in self.stages if s.name == name), None)

    def _last_running(self, stage: _Stage, kind: str) -> _ToolCall | None:
        for tc in reversed(stage.tool_calls):
            if tc.kind == kind and tc.status == "running":
                return tc
        return None

    def _apply(self, event: Event) -> None:
        stage = self._get_stage(event.node)

        if event.kind == EventKind.NODE_START:
            if stage:
                stage.status = "running"
                stage._start = event.ts
                if event.node == "specialist":
                    dept = event.data.get("dept", "")
                    stage.label = f"Specialist [{dept}]"

        elif event.kind == EventKind.NODE_DONE:
            if stage:
                stage.status = "done"
                stage.elapsed = event.ts - stage._start
            analysis = event.data.get("analysis", "")
            if analysis:
                self.analysis = analysis

        elif event.kind == EventKind.VECTOR_SEARCH_START:
            if stage:
                stage.tool_calls.append(
                    _ToolCall("vector", f"vector  ·  {event.data.get('query', '')[:60]}")
                )

        elif event.kind == EventKind.VECTOR_SEARCH_DONE:
            if stage:
                tc = self._last_running(stage, "vector")
                if tc:
                    tc.status = "done"
                    for r in event.data.get("results", [])[:4]:
                        score = r.get("score", 0)
                        meta = r.get("metadata", {})
                        name = meta.get("service_name") or meta.get("department", "")
                        mem = r.get("memory", "")[:70]
                        tc.lines.append(f"  ✓  {name or '—':<22}  {score:.2f}  {mem}")

        elif event.kind == EventKind.GRAPH_BFS_START:
            if stage:
                label = event.data.get("label") or f"blast radius from {event.data.get('service', '...')}"
                stage.tool_calls.append(_ToolCall("graph", f"graph  ·  {label}"))

        elif event.kind == EventKind.GRAPH_BFS_DONE:
            if stage:
                tc = self._last_running(stage, "graph")
                if tc:
                    tc.status = "done"
                    kind = event.data.get("label", "")
                    service = event.data.get("service", "?")

                    if kind == "neighborhood":
                        depends_on = event.data.get("depends_on", [])
                        depended_by = event.data.get("depended_by", [])
                        dept = (event.data.get("departments") or ["?"])[0]
                        tier = event.data.get("impact", "")
                        for dep in depends_on:
                            tc.lines.append(f"  {service}  →  {dep}")
                        for src in depended_by[:6]:
                            tc.lines.append(f"  {src}  →  {service}")
                        tc.lines.append(f"  [{dept}  ·  {tier}]")

                    else:  # blast_radius
                        paths = event.data.get("paths", [])
                        affected = event.data.get("affected_services", [])
                        depts = event.data.get("departments", [])
                        impact = event.data.get("impact", "")
                        seen: set[str] = set()
                        for p in paths:
                            if len(p) >= 2:
                                key = p[-1]
                                if key not in seen:
                                    seen.add(key)
                                    tc.lines.append(f"  {'  →  '.join(p)}")
                        if affected:
                            suffix = f"  ·  {', '.join(depts)}  ·  {impact.upper()}" if depts else ""
                            tc.lines.append(f"  {len(affected)} services{suffix}")

        elif event.kind == EventKind.LLM_START:
            if stage:
                stage.tool_calls.append(
                    _ToolCall("llm", f"llm  ·  {event.data.get('label', 'generating')}")
                )

        elif event.kind == EventKind.LLM_DONE:
            if stage:
                tc = self._last_running(stage, "llm")
                if tc:
                    tc.status = "done"
                    preview = event.data.get("preview", "")
                    if preview:
                        tc.lines.append(f"  {preview[:120]}")

        elif event.kind == EventKind.ROUTING:
            self.routing = event.data.get("decision", "")
            if stage:
                stage.status = "done"
                if stage._start > 0:
                    stage.elapsed = event.ts - stage._start

    # ── Rendering ───────────────────────────────────────────────────────

    def _render_header(self) -> Panel:
        inc = self.incident
        sev = inc.severity.value
        sc = _SEV_COLORS.get(sev, "white")
        elapsed = time.time() - self._t0

        row1 = Text()
        row1.append(f"  {inc.incident_id}", style="bold")
        row1.append("   service: ", style="dim")
        row1.append(inc.service_name, style="bold cyan")
        row1.append("   severity: ", style="dim")
        row1.append(sev.upper(), style=sc)
        row1.append(f"   {elapsed:.1f}s", style="dim")

        row2 = Text(f"\n  {inc.description[:110]}", style="italic")
        row3 = Text(f"\n  symptoms: {', '.join(inc.symptoms[:5])}", style="dim")

        return Panel(Group(row1, row2, row3), border_style="red", padding=(0, 1))

    def _render_stage(self, stage: _Stage) -> Group:
        nc = _NODE_COLORS.get(stage.name) or _EXTRA_COLORS.get(stage.name, "white")
        parts: list = []

        hdr = Text()
        if stage.status == "running":
            hdr.append(f"  {_spin()} ", style=nc)
        elif stage.status == "done":
            hdr.append("  ● ", style=f"bold {nc}")
        else:
            hdr.append("  ○ ", style="dim")
        hdr.append(stage.label, style=f"bold {nc}")
        if stage.status == "done" and stage.elapsed > 0:
            hdr.append(f"  {stage.elapsed:.1f}s", style="dim")
        if stage.name == "router" and self.routing:
            hdr.append(f"   →  {self.routing}", style="dim italic")
        parts.append(hdr)

        for tc in list(stage.tool_calls):
            tc_color = _TOOL_COLORS.get(tc.kind, "white")
            tc_parts: list = []

            title_t = Text()
            if tc.status == "running":
                title_t.append(f"       {_spin()} ", style=tc_color)
            else:
                title_t.append("       ▸ ", style=tc_color)
            title_t.append(tc.title, style=tc_color)
            tc_parts.append(title_t)

            for line in list(tc.lines):
                tc_parts.append(Text(line, style="dim"))

            parts.append(Group(*tc_parts))

        parts.append(Text(""))
        return Group(*parts)

    def _render_analysis(self) -> Panel:
        if not self.analysis:
            return Panel(
                Text("  waiting for specialist analysis…", style="dim"),
                title="analysis",
                border_style="green",
            )
        lines = self.analysis.split("\n")[:16]
        return Panel(Text("\n".join(lines)), title="[bold green]analysis[/]", border_style="green")

    def __rich__(self) -> Group:
        parts: list = [self._render_header(), Text("")]
        for stage in self.stages:
            if stage.status != "pending":
                parts.append(self._render_stage(stage))
        parts.append(self._render_analysis())
        return Group(*parts)
