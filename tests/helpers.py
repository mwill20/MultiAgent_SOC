import json
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool

from aegis_soc_sessions.agent import guardrail_remote_agent, root_agent
from aegis_soc_sessions.observability import record_guardrail_response

_guardrail_handler: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None


def _default_guardrail_response(request: Dict[str, Any]) -> Dict[str, Any]:
    proposed = str(request.get("proposed_action", "MONITOR")).upper()
    if "IGNORE" in str(request).upper() and "CLOSE" in str(request).upper():
        return {
            "allow": False,
            "normalized_action": "NEEDS_MORE_INFO",
            "rationale": "Prompt injection detected; refusing forced CLOSE",
        }
    mapping = {
        "ESCALATE": "ESCALATE",
        "CLOSE": "CLOSE",
        "MONITOR": "MONITOR",
        "NEEDS_MORE_INFO": "NEEDS_MORE_INFO",
    }
    normalized = mapping.get(proposed, "MONITOR")
    return {
        "allow": True,
        "normalized_action": normalized,
        "rationale": "Mock guardrail approval",
    }


def _guardrail_tool(request: str, tool_context: Optional[ToolContext] = None) -> str:
    if isinstance(request, str):
        try:
            payload = json.loads(request)
        except Exception:
            payload = {"proposed_action": request}
    else:
        payload = request

    handler = _guardrail_handler or _default_guardrail_response
    output = handler(payload)
    if tool_context is not None:
        record_guardrail_response(tool_context.state, payload, output)
    return json.dumps(output)


_guardrail_tool.__name__ = "guardrail_agent"
_guardrail_function_tool = FunctionTool(_guardrail_tool)
_guardrail_function_tool.name = "guardrail_agent"


@contextmanager
def mock_guardrail_tool(
    response_fn: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None,
):
    global _guardrail_handler
    original_tools = list(root_agent.tools)
    _guardrail_handler = response_fn

    root_agent.tools = [
        tool
        for tool in original_tools
        if getattr(tool, "agent", None) is not guardrail_remote_agent
    ]
    root_agent.tools.append(_guardrail_function_tool)

    try:
        yield
    finally:
        root_agent.tools = original_tools
        _guardrail_handler = None
