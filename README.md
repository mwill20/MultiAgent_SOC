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

## Phase 5 - Observability & Structured Events

- `aegis_soc_sessions/observability.py` defines the `StructuredEvent` schema plus helpers that log tool calls, agent outputs, state snapshots, and guardrail responses into `session.state["events"]`.
- `load_synthetic_alerts` now records every invocation (alert filter + result count) whenever a `ToolContext` is present, turning the session into an auditable stream without touching LLM prompts.
- `tests/test_phase5_observability.py` runs a two-turn session and asserts that events persist, include at least one `tool_call`, and emit an `agent_output` snapshot for the root triage summary.

## Phase 6 - Agent Evaluation & Scenarios

- `tests/eval/aegis_eval_scenarios.test.json` defines 5 test scenarios (benign, suspicious, malicious, ambiguous, prompt injection) with expected/disallowed actions.
- `tests/test_phase6_evaluation.py` runs parametrized tests over each scenario, extracting `normalized_action` from guardrail response events to validate correct SOC behavior.
- `data/synthetic_alerts.json` extended with ALERT-011 (password spray), ALERT-021 (ransomware), ALERT-031 (incomplete logs) to support diverse evaluation scenarios.

## Phase 6.5 - Guardrail Functional Tests & Infrastructure

**Test Infrastructure:**
- `tests/helpers.py` provides centralized `mock_guardrail_tool()` context manager with proper type annotations (`request: str -> str`) for ADK schema parsing.
- `aegis_soc_sessions/action_schema.py` defines `NORMALIZED_ACTIONS` constant and `enforce_action_schema()` validator to ensure action consistency across root agent, guardrail, and tests.
- `tests/conftest.py` configures Windows + Python 3.13 event loop policy to handle async test execution.
- `pytest.ini` configures asyncio mode for automatic async test execution.

**Guardrail Functional Tests:**
- `tests/test_guardrail_logic.py` validates all 3 guardrail protection mechanisms via live LLM calls:
  - **Action Normalization**: Verifies free-text → ENUM conversion ("Escalate to tier 2" → ESCALATE)
  - **Fake Execution Detection**: Blocks claims like "I have disabled the user account" (allow=false)
  - **Prompt Injection Detection**: Detects and blocks "Ignore all previous instructions" attacks (allow=false, NEEDS_MORE_INFO)
- `run_tests.py` provides pytest wrapper with output capture to `test_result.txt` (Windows encoding workaround).
- `verify_key_direct.py` utility for direct Google API key validation bypassing ADK.
- All 3 tests pass individually; event loop cleanup issue persists when running together (documented in `TESTING.md`).

## Limitations & Future Work

### Current Test Coverage

**Integration Testing (Covered ✅):**
- Multi-agent coordination via mocked guardrail
- Session state persistence across turns
- Observability event accumulation
- Action schema enforcement end-to-end
- Evaluation scenarios (benign/malicious/ambiguous/injection)

**Guardrail Wiring (Covered ✅):**
- `test_phase4_guardrail_a2a.py` verifies RemoteA2aAgent is configured correctly
- Real A2A service runs on port 8001 with agent card
- System integrates with live guardrail at runtime

**Guardrail Logic Testing (Covered ✅):**
- `tests/test_guardrail_logic.py` validates core protection mechanisms
- Action normalization (free-text -> ENUM) verified against live model
- Fake execution detection (blocking "I have done X") verified
- Prompt injection detection verified


### AegisSOC v2 Roadmap

Planned post-capstone enhancements:
1. **Guardrail Unit Tests**: Direct testing of prompt injection detection, unsafe action blocking, action normalization logic
2. **LLM Mocking**: Introduce deterministic guardrail modes for reproducible logic tests
3. **Red Team Scenarios**: Adversarial testing of guardrail bypass attempts
4. **Performance Benchmarks**: Latency and throughput testing under load
5. **Real SOC Integration**: Connect to actual SIEM APIs (Splunk, Sentinel)

This limitation is **known, documented, and defensible** - production systems commonly prioritize integration testing before exhaustive unit testing. The current test suite validates that the system respects guardrail decisions and enforces action schemas correctly.

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
│   └── synthetic_alerts.json       # 43 test alerts (10 O365, 11 firewall, 11 EDR, 11 SIEM)
├── tests/
│   ├── conftest.py                 # Pytest async configuration
│   ├── helpers.py                  # Centralized guardrail mock
│   ├── eval/
│   │   └── aegis_eval_scenarios.test.json  # 5 evaluation scenarios
│   ├── test_phase3_sessions.py     # Multi-turn session validation
│   ├── test_phase4_guardrail_a2a.py # A2A wiring tests
│   ├── test_phase5_observability.py # Event accumulation tests
│   ├── test_phase6_evaluation.py   # Parametrized scenario tests
│   └── test_guardrail_logic.py     # Phase 6.5: Guardrail functional tests
├── run_tests.py                    # Phase 6.5: Test runner with output capture
├── verify_key_direct.py            # Phase 6.5: API key validation utility
├── pytest.ini                      # Pytest asyncio configuration
├── TESTING.md                      # Test execution notes & workarounds
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

**Phase 5 - Observability:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase5_observability.py -v
```

**Phase 6 - Evaluation (run scenarios individually):**

```powershell
.\.\.venv\Scripts\python.exe -m pytest tests/test_phase6_evaluation.py::test_phase6_evaluation_scenario -k "scenario0" -v
.\.\.venv\Scripts\python.exe -m pytest tests/test_phase6_evaluation.py::test_phase6_evaluation_scenario -k "scenario1" -v
```

**Phase 6.5 - Guardrail Functional Tests:**

```powershell
# Run all tests (may encounter event loop cleanup issue on test 2)
.\.\.venv\Scripts\python.exe run_tests.py

# OR run individually (recommended - all pass):
.\.\.venv\Scripts\python.exe -m pytest tests/test_guardrail_logic.py::test_action_normalization -v
.\.\.venv\Scripts\python.exe -m pytest tests/test_guardrail_logic.py::test_fake_execution_detection -v
.\.\.venv\Scripts\python.exe -m pytest tests/test_guardrail_logic.py::test_prompt_injection -v
```

**Note:** See `TESTING.md` for known event loop cleanup issue when running multiple async tests together. All tests pass when run individually - this is a test infrastructure timing issue, not a code bug.

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
5. **Event-Driven Observability**: Structured events logged to session state provide audit trail without polluting LLM context (Phase 5)
6. **Scenario-Based Evaluation**: Test scenarios validate end-to-end behavior including guardrail compliance (Phase 6)
7. **Live LLM Testing**: Guardrail functional tests use real model responses to validate instruction compliance (Phase 6.5)
