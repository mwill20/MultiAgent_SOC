"""
Phase 2 end-to-end test using the InMemoryRunner.run_debug() API.
Bypasses the ADK CLI runner to test agent behavior programmatically.
"""
import asyncio
import os
import sys
from pathlib import Path

# Load environment variables from aegis_soc_app/.env
env_file = Path(__file__).parent / "aegis_soc_app" / ".env"
if env_file.exists():
    with env_file.open() as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Add aegis_soc_app to path
sys.path.insert(0, str(Path(__file__).parent / "aegis_soc_app"))

from agent import app
from google.adk.runners import InMemoryRunner

async def test_phase2_triage():
    """Test multi-agent triage using InMemoryRunner.run_debug()."""
    print("=" * 80)
    print("Phase 2 Multi-Agent Triage Test")
    print("=" * 80)
    
    prompt = "Triage all alerts and identify any correlated activity"
    print(f"\n[USER PROMPT]: {prompt}\n")
    
    # Create runner and use run_debug() - it's async!
    print("[CREATING RUNNER...]")
    runner = InMemoryRunner(app=app)
    
    print("[EXECUTING AGENT...]")
    print("(This may take 30-60 seconds...)\n")
    events = await runner.run_debug(prompt)
    
    # Extract text from events (run_debug returns a list of Event objects)
    response_text = ""
    for event in events:
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text + "\n"
    
    print("\n" + "=" * 80)
    print("AGENT RESPONSE:")
    print("=" * 80)
    print(response_text)
    print("\n" + "=" * 80)
    
    # Basic validation
    assert events is not None and len(events) > 0, "No events returned"
    assert len(response_text) > 0, "No text in response"
    
    # Check for evidence of multi-agent behavior
    response_lower = response_text.lower()
    checks = {
        "Mentions alerts": any(word in response_lower for word in ["alert", "synthetic"]),
        "Shows severity awareness": any(sev in response_lower for sev in ["high", "medium", "low"]),
        "Discusses correlation": any(word in response_lower for word in ["correlat", "pattern", "relationship", "connect"]),
        "No execution claims": not any(claim in response_lower for claim in ["i have blocked", "i have disabled", "i executed"])
    }
    
    print("\n" + "=" * 80)
    print("VALIDATION CHECKS:")
    print("=" * 80)
    for check, passed in checks.items():
        status = "✅" if passed else "⚠️"
        print(f"{status} {check}")
    
    all_passed = all(checks.values())
    
    if all_passed:
        print("\n✅ Phase 2 end-to-end test PASSED")
    else:
        print("\n⚠️  Phase 2 test completed with warnings")
    
    print(f"✅ Response length: {len(response_text)} characters")
    print(f"✅ Events captured: {len(events)}")
    
    return response_text

if __name__ == "__main__":
    try:
        asyncio.run(test_phase2_triage())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
