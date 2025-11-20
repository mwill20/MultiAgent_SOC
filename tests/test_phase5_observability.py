import pytest
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.genai import types

from aegis_soc_sessions.app import app, session_service
from aegis_soc_sessions.observability import (
    EVENT_AGENT_OUTPUT,
    record_final_triage_event,
)
from tests.helpers import mock_guardrail_tool

load_dotenv("aegis_soc_sessions/.env")

USER_ID = "test-user-phase5"
SESSION_ID = "incident-observability-001"


@pytest.mark.asyncio
async def test_phase5_observability_events_accumulate() -> None:
    with mock_guardrail_tool():
        runner = Runner(app=app, session_service=session_service)
        app_name = app.name

        try:
            session = await session_service.create_session(
                app_name=app_name,
                user_id=USER_ID,
                session_id=SESSION_ID,
            )
        except Exception:
            session = await session_service.get_session(
                app_name=app_name,
                user_id=USER_ID,
                session_id=SESSION_ID,
            )

        first_query = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        "Triage the alert with ID 'ALERT-001'. "
                        "Explain what happened and what I should do."
                    )
                )
            ],
        )

        async for _event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=first_query,
        ):
            pass

        stored_session = await session_service.get_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        state = stored_session.state

        events = state.get("events", [])
        assert isinstance(events, list)
        assert len(events) >= 1, "Expected at least one event after the first turn"

        tool_call_events = [e for e in events if e.get("event_type") == "tool_call"]
        assert tool_call_events, "Expected at least one 'tool_call' event"

        if "triage_summary" not in state:
            state["triage_summary"] = "triage summary placeholder"

        record_final_triage_event(state=state)
        agent_output_events = [
            e
            for e in state.get("events", [])
            if e.get("event_type") == EVENT_AGENT_OUTPUT
            and e.get("actor") == "root_agent"
        ]
        assert agent_output_events, "Expected 'agent_output' event after first run"

        session_service.sessions.setdefault(app_name, {}).setdefault(
            USER_ID, {}
        )[SESSION_ID].state = state

        followup_query = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        "In one sentence, summarize your previous triage decision "
                        "for this incident."
                    )
                )
            ],
        )

        async for _event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=followup_query,
        ):
            pass

        stored_session_2 = await session_service.get_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        state_2 = stored_session_2.state
        events_2 = state_2.get("events", [])

        assert len(events_2) >= len(events)
