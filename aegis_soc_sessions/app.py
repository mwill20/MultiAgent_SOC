from google.adk.apps.app import App
from google.adk.sessions import InMemorySessionService

from .agent import correlation_agent, log_parser_agent, root_agent

# Session service: short-lived, in-memory, per-incident sessions
session_service = InMemorySessionService()

app = App(
    name="aegis_soc_sessions",
    root_agent=root_agent,
)
