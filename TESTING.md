# TESTING.md — AegisSOC Test Guide

AegisSOC includes a **layered testing strategy** designed to validate:

- Multi-agent wiring  
- Session and state persistence  
- Structured observability  
- Guardrail behavior (mock + real LLM)  
- Scenario-driven evaluation  

All tests use Python `pytest` and are compatible with ADK 1.18.0.

---

## 1. Test Categories

AegisSOC includes four major categories of tests:

### 1.1 Phase 3 — Session & State Tests
Validates:
- InMemorySessionService
- Stateful agent execution
- Multi-turn interactions

File: `tests/test_phase3_sessions.py`

Run:
```powershell
python -m pytest tests/test_phase3_sessions.py -q
```

### 1.2 Phase 5 — Observability Tests
Validates:
- StructuredEvent model
- State["events"] correctness
- Logging of tool calls, agent outputs, guardrail responses

File: `tests/test_phase5_observability.py`

Run:
```powershell
python -m pytest tests/test_phase5_observability.py -q
```

### 1.3 Phase 6 — Evaluation Scenarios
Validates:
- System behavior against benign, suspicious, malicious, ambiguous, and prompt-injection scenarios
- Use of observability for verifying output

File: `tests/test_phase6_evaluation.py`

Run:
```powershell
python -m pytest tests/test_phase6_evaluation.py -q
```

**Note:**  
If the LLM produces no final action in a scenario, the test may be skipped or marked xfail. This is documented and expected due to LLM variance.

### 1.4 Phase 6.5 — Guardrail Functional Tests (Live LLM)
Validates the actual guardrail microservice with real reasoning:
- Action Normalization
- Fake Execution Detection
- Prompt Injection Detection

File: `tests/test_guardrail_logic.py`

**Prerequisite:** Ensure guardrail microservice is running first:
```powershell
python -m guardrail_agent.app
```

Run:
```powershell
python -m pytest tests/test_guardrail_logic.py -q
```

These tests hit the Guardrail Agent (A2A microservice) at `localhost:8001`.

---

## 2. Running All Tests (Individual Runs Recommended)

Due to a known asyncio / httpx event loop cleanup issue in:
- Windows
- Python 3.13
- pytest-asyncio

…it is recommended to run tests individually:

```powershell
python -m pytest tests/test_phase3_sessions.py -q
python -m pytest tests/test_phase5_observability.py -q
python -m pytest tests/test_phase6_evaluation.py -q
python -m pytest tests/test_guardrail_logic.py -q
```

---

## 3. Using run_tests.py

For convenience:

```powershell
python run_tests.py
```

This script:
- Runs pytest programmatically
- Captures output to `test_result.txt`
- Improves reliability on Windows

---

## 4. Expected Outputs

| Phase | File | Expected Result |
|-------|------|----------------|
| Phase 3 | test_phase3_sessions.py | 1 PASSED |
| Phase 5 | test_phase5_observability.py | 1 PASSED |
| Phase 6 | test_phase6_evaluation.py | PASS / SKIP (depending on LLM output) |
| Phase 6.5 | test_guardrail_logic.py | 3 PASSED individually |

---

## 5. Troubleshooting

**Event loop closed:**
```
RuntimeError: Event loop is closed
```
- Harmless
- Related to async teardown
- Run tests individually

**Guardrail not reachable:**

Ensure guardrail microservice is running:
```powershell
python -m guardrail_agent.app
```

**Invalid / missing API key:**

Check `.env`:
```env
GOOGLE_API_KEY=your_api_key_here
```

---

## 6. Summary

AegisSOC's testing framework covers:
- structural correctness
- safety boundaries
- LLM normalization behavior
- injection detection
- system-wide evaluation

This layered strategy is aligned with best practices in AI security engineering.
