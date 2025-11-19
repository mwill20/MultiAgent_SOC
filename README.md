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

## Phase 4 - Guardrail Agent (A2A)

- `guardrail_agent/` hosts a dedicated Guardrail Agent exposed over A2A (`to_a2a`), enforcing the action enum `ESCALATE | MONITOR | CLOSE | NEEDS_MORE_INFO`.
- `aegis_soc_sessions/agent.py` now loads a `RemoteA2aAgent` sub-agent so the root triage workflow must call the Guardrail before finalizing recommendations.
- `tests/test_phase4_guardrail_a2a.py` verifies the remote guardrail wiring without needing the external service live.

**Running the Guardrail Service:**
```powershell
cd c:\Projects\Google5Day\aegis-soc
& .\.venv\Scripts\python.exe -m guardrail_agent.app
```
Service runs on `http://127.0.0.1:8001` with agent card at `/.well-known/agent-card.json`.

## Project Structure

```
aegis-soc/
├── .venv/                          # Python virtual environment
├── aegis_soc_app/                  # Phase 1-2: Single & multi-agent baseline
│   ├── agent.py                    # Root, LogParser, Correlation agents
│   ├── app.py                      # ADK app configuration
│   └── .env                        # API key configuration
├── aegis_soc_sessions/             # Phase 3: Session-aware agents
│   ├── agent.py                    # State-persistent agent stack
│   ├── app.py                      # App with InMemorySessionService
│   └── .env                        # API key (separate from aegis_soc_app)
├── guardrail_agent/                # Phase 4: A2A guardrail service
│   ├── agent.py                    # LlmAgent with action enforcement
│   ├── app.py                      # A2A service wrapper (port 8001)
│   └── __init__.py                 # Package exports
├── data/
│   └── synthetic_alerts.json       # 40 test alerts (10 each: O365, firewall, EDR, SIEM)
├── tests/
│   ├── test_phase3_sessions.py     # Multi-turn session validation
│   └── test_phase4_guardrail_a2a.py # A2A wiring tests
└── README.md
```

## Testing

**Phase 3 - Session State:**
```powershell
$env:GOOGLE_API_KEY = (Get-Content aegis_soc_sessions\.env | Select-String 'GOOGLE_API_KEY' | ForEach-Object { $_.Line.Split('=')[1] })
.\.venv\Scripts\python.exe -m pytest tests/test_phase3_sessions.py -v
```

**Phase 4 - Guardrail Wiring:**
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase4_guardrail_a2a.py -v
```

## Requirements

- Python 3.13.5
- Google ADK 1.18.0
- a2a-sdk 0.3.14
- pytest 9.0.1 (with pytest-asyncio)
- uvicorn 0.38.0
- Valid Google API key (Gemini 2.5 Flash-Lite)

## Known Issues

- ADK 1.18.0 CLI has session bug with Python 3.13.5 - use `Runner` or `InMemoryRunner.run_debug()` programmatically
- RemoteA2aAgent is EXPERIMENTAL (warnings expected)

## Architecture Decisions

1. **Multi-Agent Separation**: LogParser and Correlation agents focus on specific tasks, reducing prompt complexity
2. **Session State Management**: `ToolContext.state` and `output_key` attributes persist data across conversation turns
3. **A2A Guardrail**: Separate service enforces policy without coupling to triage logic
4. **Action Enum**: `ALLOWED_ACTIONS` constant shared between guardrail and client ensures contract consistency
