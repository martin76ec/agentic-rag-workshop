"""
Exercise 3.1 — Triage classifier
================================
The triage agent asks the LLM to return JSON like:

    {"service_name": "...", "severity_classification": "...", "department": "..."}

But the LLM sometimes wraps the JSON in markdown fences (```json ... ```),
sometimes adds a leading sentence, and sometimes returns invalid JSON. The
current parser doesn't handle any of that — it falls through to the
hardcoded "platform" fallback for almost every incident.

Fix: write a tolerant parser that:
  1. Strips markdown code fences if present.
  2. Extracts the first balanced JSON object from the text.
  3. Validates the `severity_classification` against the Severity enum.
  4. Validates the `department` against the Department enum.
"""
import json
from typing import Any

from src.infrastructure.models import Department, Severity


def parse_classification(llm_response: str) -> dict[str, Any]:
    """Parse the LLM's classification text into a validated dict.

    Returns a dict with keys:
        service_name (str)
        severity (Severity)
        department (Department)
        reasoning (str)
    """
    # TODO 3.1.a — strip markdown code fences. The LLM often wraps JSON in
    # triple backticks: ```json ... ``` or ``` ... ```.
    cleaned = llm_response.strip()

    # TODO 3.1.b — extract the first balanced { ... } block. Use a regex or
    # a depth counter. Some LLM responses include prose before the JSON.
    json_text = cleaned

    # Parse — should be tolerant of trailing prose AFTER the JSON object.
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        data = {}

    # TODO 3.1.c — validate severity. Coerce to Severity enum, fallback to MEDIUM.
    severity = Severity.MEDIUM  # TODO

    # TODO 3.1.d — validate department. Coerce to Department enum, fallback
    # to PLATFORM only if no valid value was provided. Crucially, do NOT
    # default to PLATFORM if a valid department was returned.
    department = Department.PLATFORM  # TODO

    return {
        "service_name": data.get("service_name", "unknown"),
        "severity": severity,
        "department": department,
        "reasoning": data.get("reasoning", ""),
    }
