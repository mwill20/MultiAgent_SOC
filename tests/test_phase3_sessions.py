import pytest
from dotenv import load_dotenv

from google.adk.errors.already_exists_error import AlreadyExistsError
from google.adk.runners import Runner
from google.genai import types

from aegis_soc_sessions.app import app, session_service
from tests.helpers import mock_guardrail_tool

load_dotenv("aegis_soc_sessions/.env")

USER_ID = "test-user-phase3"


@pytest.mark.asyncio
async def test_phase3_single_session_accumulates_events():
    with mock_guardrail_tool():
        runner = Runner(app=app, session_service=session_service)
        app_name = app.name
        session_name = "incident-001"

        try:
            session = await session_service.create_session(
                app_name=app_name,
                user_id=USER_ID,
                session_id=session_name,
            )
        except AlreadyExistsError:
            session = await session_service.get_session(
                app_name=app_name,
                user_id=USER_ID,
                session_id=session_name,
            )
            assert session is not None

        first_query = types.Content(
            role="user",
            parts=[
                types.Part(
                    text="Triage the alert with ID 'ALERT-001'. "
                    "Explain what happened and what I should do."
                )
            ],
        )

        async for _event in runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=first_query,
        ):
            pass

        followup_query = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        "Summarize the prior triage decision for this incident "
                        "in 2 sentences."
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

        stored_session = await session_service.get_session(
            app_name=app_name,
            user_id=USER_ID,
            session_id=session_name,
        )

        assert stored_session is not None
        assert len(stored_session.events) >= 2
        assert "triage_summary" in stored_session.state
