from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from google.adk.agents.llm_agent import Agent
from google.adk.apps import App


class RootTriageAgent(Agent):
    """
    Root coordinator and triage agent for the AegisSOC multi-agent pipeline.
    Receives user questions, delegates work conceptually to specialized
    sub-agents, and composes the final SOC-facing response.
    """


class LogParserAgent(Agent):
    """
    Specialized agent for parsing and normalizing synthetic alerts.
    Focuses on structure: fields, schemas, and key indicators per alert.
    """


class CorrelationAgent(Agent):
    """
    Specialized agent for finding relationships and patterns across alerts.
    Focuses on cross-alert context, timelines, and campaign-style thinking.
    """


def load_synthetic_alerts() -> List[Dict[str, Any]]:
    """Load synthetic SOC alerts from the local data file.

    Returns:
        List[Dict[str, Any]]: Alert dictionaries with fields such as:
            - id (str): Unique alert identifier (e.g., "ALERT-001")
            - source (str): Alert origin (e.g., "o365", "firewall", "edr", "siem")
            - severity (str): Risk level label ("high", "medium", "low")
            - category (str): Threat classification (e.g., "suspicious_login")
            - timestamp (str): ISO 8601 timestamp
            - Additional fields vary per source (username, ip, hostname, etc.)

    Security:
        - Reads only checked-in synthetic data; no external calls occur.
        - Never mixes or accesses real customer data.

    Raises:
        FileNotFoundError: If data/synthetic_alerts.json does not exist.
        ValueError: If the JSON payload is not a list of alerts.
    """
    base_dir = Path(__file__).resolve().parent.parent
    alerts_path = base_dir / "data" / "synthetic_alerts.json"

    if not alerts_path.exists():
        raise FileNotFoundError(f"Synthetic alerts file not found: {alerts_path}")

    with alerts_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Synthetic alerts file must contain a JSON list of alerts.")

    return data


log_parser_agent = LogParserAgent(
    model="gemini-2.5-flash-lite",
    name="log_parser_agent",
    tools=[load_synthetic_alerts],
    description=(
        "Log Parser Agent for AegisSOC. Uses synthetic alert data to identify "
        "fields, normalize schemas across sources (O365, firewall, EDR, SIEM), "
        "and highlight key indicators per alert."
    ),
    instruction=(
        "You are a log parsing specialist for AegisSOC. Your job is to read the "
        "synthetic alerts via the load_synthetic_alerts tool and produce a clear, "
        "structured view of each alert. Focus on: id, source, severity, category, "
        "timestamp, and any notable fields (username, src_ip, hostname, etc.). "
        "Call out differences between sources (e.g., O365 vs. firewall vs. EDR vs. SIEM). "
        "Do NOT perform full triage or recommend actions; simply normalize and explain "
        "the data in a way a SOC analyst can consume."
    ),
)


correlation_agent = CorrelationAgent(
    model="gemini-2.5-flash-lite",
    name="correlation_agent",
    tools=[load_synthetic_alerts],
    description=(
        'Correlation Agent for AegisSOC. Looks for relationships between alerts, '
        'such as shared entities, timing patterns, or likely campaign activity.'
    ),
    instruction=(
        "You are a correlation specialist for AegisSOC. Use the synthetic alerts "
        "from load_synthetic_alerts to look for relationships across alerts. "
        "Examples include: same username across multiple alerts, same IP hitting "
        "different systems, or a logical timeline of attack stages. Summarize any "
        "likely connections or note explicitly when alerts appear unrelated. "
        "Do NOT invent new alerts or entities; stay strictly within the loaded data."
    ),
)


root_agent = RootTriageAgent(
    model="gemini-2.5-flash-lite",
    name="root_agent",
    tools=[load_synthetic_alerts],
    sub_agents=[log_parser_agent, correlation_agent],
    description=(
        "Root SOC triage coordinator for AegisSOC. Receives analyst questions, "
        "uses synthetic alert data, and conceptually delegates parsing to the "
        "Log Parser Agent and cross-alert reasoning to the Correlation Agent "
        "before composing a final SOC triage summary."
    ),
    instruction=(
        "You are the root SOC triage coordinator for AegisSOC, working with "
        "synthetic alerts only. Alert schemas vary by source (O365, firewall, "
        "EDR, SIEM). When users ask about alert structure or raw content, rely "
        "on the Log Parser Agent's perspective. When they ask about relationships "
        "or campaigns, rely on the Correlation Agent's perspective. "
        "Always ground your answers in the output of the load_synthetic_alerts "
        "tool and never invent additional alerts or fake evidence. "
        "Your job is to provide a concise, SOC-ready triage summary that brings "
        "together parsing and correlation: context, analysis, risk, and "
        "recommended next steps. Never claim to touch real systems or execute "
        "containment; you only provide analysis and recommendations on synthetic data."
    ),
)


app = App(
    name="aegis_soc_multi_agent_baseline",
    root_agent=root_agent,
)
