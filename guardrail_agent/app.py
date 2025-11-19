from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import guardrail_agent

# FastAPI/Starlette A2A app
app = to_a2a(guardrail_agent, port=8001)


if __name__ == "__main__":
  # Optional convenience entry point for local testing:
  #   python -m guardrail_agent.app
  import uvicorn

  uvicorn.run("guardrail_agent.app:app", host="127.0.0.1", port=8001, reload=False)
