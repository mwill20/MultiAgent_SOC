from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


# Basic retry config for Gemini
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def _load_alerts_file() -> List[Dict[str, Any]]:
    """Internal helper to load the synthetic alerts JSON from ../data/."""
    data_path = Path(__file__).resolve().parents[1] / "data" / "synthetic_alerts.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_synthetic_alerts(
    alert_id: Optional[str] = None,
    tool_context: ToolContext | None = None,
) -> List[Dict[str, Any]]:
    """
    Load synthetic SOC alerts from local JSON for analysis.

    This tool is *read-only* and only works with synthetic data shipped
    with the AegisSOC repo.

    Args:
        alert_id: Optional ID to filter on. If provided, only alerts whose
                  'id' field matches (string compare) are returned.
        tool_context:  ToolContext from ADK. When present, this function will
                  store the loaded alerts into session state under the key
                  'raw_alerts' so other agents can reuse them.

    Returns:
        A list of alert dictionaries.
    """
    alerts = _load_alerts_file()

    if alert_id:
        filtered = [a for a in alerts if str(a.get("id")) == str(alert_id)]
    else:
        filtered = alerts

    if tool_context is not None:
        # Make the raw alerts available to other tools/agents in this session.
        tool_context.state["raw_alerts"] = filtered

    return filtered


load_synthetic_alerts_tool = FunctionTool(load_synthetic_alerts)


# --- Sub-agents --------------------------------------------------------------


log_parser_agent = LlmAgent(
    name="log_parser_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Parses raw SOC alerts into a human-readable explanation.",
    instruction="""
You are a SOC log parsing specialist.

You receive raw security alerts as JSON in {raw_alerts?}.
Your job is to explain clearly:

- What happened
- Who or what was involved (user, IP, host, device)
- Why the alert likely fired

Write in concise language that a Tier 1 analyst can understand.
""",
    # Store this agent's output into session state so it can be reused.
    output_key="parsed_alerts",
)


correlation_agent = LlmAgent(
    name="correlation_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Looks for relationships across multiple alerts.",
    instruction="""
You are a SOC correlation specialist.

You are given a human-readable description of one or more alerts in {parsed_alerts?}.
If there is only one alert, explain that clearly.
If there are multiple alerts, look for patterns, such as:

- Same user across multiple alerts
- Same IP or host involved
- Time proximity that suggests a campaign or sequence

Summarize any correlations and describe whether this looks like:
- a single isolated event, or
- part of a broader pattern / campaign.

Keep the answer short (1–2 paragraphs).
""",
    output_key="correlation_summary",
)


# --- Root triage agent -------------------------------------------------------


root_agent = LlmAgent(
    name="root_triage_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Top-level SOC triage agent for AegisSOC.",
    instruction="""
You are the primary SOC triage agent in the AegisSOC system.

You have three main capabilities:
- 'load_synthetic_alerts' tool to fetch synthetic security alerts
- 'log_parser_agent' to convert raw alerts into human-readable explanations
- 'correlation_agent' to connect related alerts into a bigger picture

ALWAYS follow this flow:

1) Call 'load_synthetic_alerts' first.
   - If the user mentions a specific alert ID, pass it as alert_id.
   - Otherwise, load the relevant alerts for the query.

2) Use 'log_parser_agent' to turn {raw_alerts?} into an explanation.
   - Its output will be stored in session state under 'parsed_alerts'.

3) If there are multiple alerts or the situation looks noisy,
   call 'correlation_agent' to get a higher-level view.
   - Its output will be stored under 'correlation_summary'.

4) Produce a final triage summary that includes:
   - What happened (short narrative)
   - Likely risk level: Low, Medium, or High
   - Recommended action: Escalate, Monitor, or Close
   - Brief justification for your recommendation

5) Remember that your final answer is stored in the 'triage_summary'
   state key so the analyst can ask follow-up questions in the same
   session without redoing all the work.

GUARDRAILS:
- You are analysis-only. Never claim to have actually taken containment
  or configuration actions (blocking IPs, disabling accounts, etc.).
- If information is missing or ambiguous, say so explicitly and choose
  the safest reasonable recommendation.
""",
    tools=[
        load_synthetic_alerts_tool,
        AgentTool(agent=log_parser_agent),
        AgentTool(agent=correlation_agent),
    ],
    # Store the full triage answer in session state.
    output_key="triage_summary",
)
