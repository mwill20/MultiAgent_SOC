from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from aegis_soc_sessions.agent import ALLOWED_ACTIONS, root_agent


def test_root_agent_has_remote_guardrail_subagent() -> None:
    # Check that guardrail is wrapped in an AgentTool in the tools list
    guardrail_agent_tools = [
        tool for tool in root_agent.tools 
        if hasattr(tool, 'agent') and isinstance(tool.agent, RemoteA2aAgent)
    ]
    assert (
        guardrail_agent_tools
    ), "Expected at least one AgentTool wrapping RemoteA2aAgent in root_agent.tools"
    
    guardrail_agent_tool = guardrail_agent_tools[0]
    guardrail = guardrail_agent_tool.agent
    agent_card_source = getattr(guardrail, "_agent_card_source", "")
    assert isinstance(agent_card_source, str)
    assert ".well-known/agent-card.json" in agent_card_source


def test_allowed_actions_enum_is_defined() -> None:
  assert set(ALLOWED_ACTIONS) == {"ESCALATE", "MONITOR", "CLOSE", "NEEDS_MORE_INFO"}
