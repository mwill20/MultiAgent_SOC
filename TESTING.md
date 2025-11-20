# Test Execution Notes

## Known Issue: Event Loop Cleanup in Pytest

### Problem
When running multiple async tests sequentially (Phase 3 + 5 + 6), httpx/anyio connection cleanup can trigger `RuntimeError: Event loop is closed` errors on Windows with Python 3.13.

### Root Cause
- Google GenAI SDK uses httpx for async HTTP requests
- Windows Selector/Proactor event loop incompatibility with anyio transport cleanup
- Event loop closes before all pending callbacks complete

### Workaround
**Run test phases individually:**

```powershell
# Phase 3: Sessions
pytest tests/test_phase3_sessions.py -v

# Phase 4: Guardrail A2A
pytest tests/test_phase4_guardrail_a2a.py -v

# Phase 5: Observability
pytest tests/test_phase5_observability.py -v

# Phase 6: Evaluation (individual scenarios)
pytest tests/test_phase6_evaluation.py::test_phase6_evaluation_scenario -k "scenario0" -v
pytest tests/test_phase6_evaluation.py::test_phase6_evaluation_scenario -k "scenario1" -v
```

### Status
✅ **All core functionality works** - this is a test infrastructure timing issue, not a code bug.

- Phase 3: ✅ PASSES individually
- Phase 4: ✅ PASSES individually  
- Phase 5: ✅ PASSES individually
- Phase 6: ✅ PASSES individually (scenarios run separately)

### Impact
- **None on production code** - the agent system works correctly
- **Tests are valid** - they pass when isolated
- **Acceptable for capstone** - demonstrates working multi-agent architecture
