# AegisSOC - Secure Multi-Agent SOC Assistant

This repository contains the AegisSOC Kaggle Capstone project:
a secure multi-agent SOC triage assistant built with Google ADK and Gemini.

## Phase 1 - Single-Agent Baseline

- Synthetic triage data lives in `data/synthetic_alerts.json` and now includes ten O365, ten firewall, ten EDR, and ten SIEM alerts to drive richer tooling tests.
- `aegis_soc_app/agent.py` defines the `load_synthetic_alerts` tool plus the `root_agent`, which always inspects the dataset before answering.
- The ADK app `aegis_soc_single_agent` exposes this baseline agent; upcoming phases add multi-agent routing, sessions, guardrails, and evaluation assets.

## Phase 2 - Multi-Agent Wiring

- `aegis_soc_app/agent.py` wires a RootTriageAgent with LogParserAgent and CorrelationAgent sub-agents, all sharing the `load_synthetic_alerts` tool via the `aegis_soc_multi_agent_baseline` app to mirror real SOC specialization.
- The architecture keeps responsibilities separated (parsing vs. correlation) while the root agent composes a SOC-facing summary.

## Phase 3 - Sessions & State

- `aegis_soc_sessions/` introduces a session-aware app that chains tool + sub-agents through ADK `LlmAgent` output keys so parsed alerts, correlations, and final triage summaries persist across incident turns via `InMemorySessionService`.
- `tests/test_phase3_sessions.py` drives two turns in the same session to ensure state accumulation and guardrail-friendly follow-up behavior.
