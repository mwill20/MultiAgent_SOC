from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from aegis_soc_sessions.agent import ALLOWED_ACTIONS, root_agent


def test_root_agent_has_remote_guardrail_subagent() -> None:
  guardrail_subagents = [
      agent for agent in root_agent.sub_agents if isinstance(agent, RemoteA2aAgent)
  ]
  assert (
      guardrail_subagents
  ), "Expected at least one RemoteA2aAgent as a sub-agent on root_agent"

  guardrail = guardrail_subagents[0]
  agent_card_source = getattr(guardrail, "_agent_card_source", "")
  assert isinstance(agent_card_source, str)
  assert ".well-known/agent-card.json" in agent_card_source


def test_allowed_actions_enum_is_defined() -> None:
  assert set(ALLOWED_ACTIONS) == {"ESCALATE", "MONITOR", "CLOSE", "NEEDS_MORE_INFO"}
