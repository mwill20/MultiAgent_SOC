# AegisSOC - Secure Multi-Agent SOC Assistant

This repository contains the AegisSOC:
a secure multi-agent SOC triage assistant built with Google ADK and Gemini.

## Phase 2 - Multi-Agent Baseline

- **Architecture**: Root coordinator (`RootTriageAgent`) delegates to two specialized sub-agents:
  - `LogParserAgent`: Normalizes alert schemas and extracts key fields
  - `CorrelationAgent`: Identifies relationships and patterns across alerts
- **Data**: Synthetic triage data in `data/synthetic_alerts.json` contains 40 alerts (10 each: O365, firewall, EDR, SIEM)
- **Shared Tool**: All agents use `load_synthetic_alerts()` for consistent data access
- **App**: `aegis_soc_multi_agent_baseline` orchestrates the three-agent pipeline
- **Upcoming**: Phase 3 adds session/state wiring, Phase 4 guardrails, Phase 5 evaluation assets
