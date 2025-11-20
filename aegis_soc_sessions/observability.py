from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List


EVENT_TOOL_CALL = "tool_call"
EVENT_AGENT_CALL = "agent_call"
EVENT_AGENT_OUTPUT = "agent_output"
EVENT_STATE_CHANGE = "state_change"
EVENT_STATE_SNAPSHOT = "state_snapshot"
EVENT_GUARDRAIL_RESPONSE = "guardrail_response"


@dataclass
class StructuredEvent:
    timestamp: str
    event_type: str
    actor: str
    details: Dict[str, Any]


def _get_or_init_events(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ensure state['events'] exists and is a list, then return it.
    This is our central, structured event stream per session.
    """
    events = state.get("events")
    if events is None:
        events = []
        state["events"] = events
    return events


def record_event(
    state: Dict[str, Any],
    event_type: str,
    actor: str,
    details: Dict[str, Any] | None = None,
) -> None:
    """
    Append a StructuredEvent into state['events'].

    - event_type: 'tool_call', 'agent_output', 'state_update', etc.
    - actor: which tool/agent produced this event.
    - details: JSON-serializable dictionary with context.
    """
    if details is None:
        details = {}

    events = _get_or_init_events(state)
    event = StructuredEvent(
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=event_type,
        actor=actor,
        details=details,
    )
    events.append(asdict(event))


def record_state_snapshot(
    state: Dict[str, Any],
    actor: str,
    keys_to_track: List[str],
) -> None:
    """
    Convenience helper to log a snapshot of selected state keys.

    Example:
        record_state_snapshot(state, "root_agent", ["raw_alerts", "parsed_alerts"])
    """
    snapshot = {key: state.get(key) for key in keys_to_track}
    record_event(
        state=state,
        event_type=EVENT_STATE_SNAPSHOT,
        actor=actor,
        details={"state": snapshot},
    )


def record_final_triage_event(state: Dict[str, Any]) -> None:
    """
    If 'triage_summary' exists in state, log it as an 'agent_output' event
    for 'root_agent'. Safe to call at the end of a test run.
    """
    if "triage_summary" not in state:
        return

    triage = state.get("triage_summary")
    record_event(
        state=state,
        event_type=EVENT_AGENT_OUTPUT,
        actor="root_agent",
        details={"triage_summary": triage},
    )


def record_guardrail_response(
    state: Dict[str, Any],
    guardrail_input: Dict[str, Any],
    guardrail_output: Dict[str, Any],
) -> None:
    """Log a guardrail validation decision for auditability."""
    record_event(
        state=state,
        event_type=EVENT_GUARDRAIL_RESPONSE,
        actor="guardrail_remote_agent",
        details={"input": guardrail_input, "output": guardrail_output},
    )
