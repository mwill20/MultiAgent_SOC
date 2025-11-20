"""Shared action schema for SOC triage system."""

NORMALIZED_ACTIONS = {"ESCALATE", "MONITOR", "CLOSE", "NEEDS_MORE_INFO"}


def enforce_action_schema(action: str) -> str:
    """Ensure action is in allowed set, fallback to NEEDS_MORE_INFO."""
    if action not in NORMALIZED_ACTIONS:
        return "NEEDS_MORE_INFO"
    return action
