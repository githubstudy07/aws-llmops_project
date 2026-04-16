# File: tests/test_agents.py
"""エージェント統合テスト"""

from __future__ import annotations

from crew_app.agents import make_researcher
from crew_app.tools import DuckDuckGoSearchTool


class TestMakeResearcher:
    """make_researcher 関数のテスト"""

    def test_returns_agent_with_tools(self) -> None:
        """Researcher エージェントにツールが含まれていることを検証"""
        agent = make_researcher()
        assert agent is not None
        assert len(agent.tools) >= 1
        assert any(
            isinstance(t, DuckDuckGoSearchTool) for t in agent.tools
        )

    def test_agent_role(self) -> None:
        """エージェントの role が設定されていることを検証"""
        agent = make_researcher()
        assert "Research" in agent.role
