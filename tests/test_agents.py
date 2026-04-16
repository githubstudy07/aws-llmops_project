# tests/test_agents.py
"""
エージェント生成関数のユニットテスト
旧関数名 make_researcher → create_researcher_agent に更新済み
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# 環境変数をテスト用に設定
os.environ.setdefault("BEDROCK_MODEL_ID", "us.amazon.nova-micro-v1:0")
os.environ.setdefault("WRITES_TABLE", "handson-research-archives") # 本計画でのテーブル名


@patch("crew_app.agents._get_llm")
def test_create_researcher_agent(mock_llm):
    """create_researcher_agent が Agent インスタンスを返すことを確認"""
    mock_llm.return_value = MagicMock()
    from crew_app.agents import create_researcher_agent
    agent = create_researcher_agent()
    assert agent is not None
    assert agent.role == "Senior Research Analyst"


@patch("crew_app.agents._get_llm")
def test_create_writer_agent(mock_llm):
    """create_writer_agent が Agent インスタンスを返すことを確認"""
    mock_llm.return_value = MagicMock()
    from crew_app.agents import create_writer_agent
    agent = create_writer_agent()
    assert agent is not None
    assert agent.role == "Creative Copywriter"


@patch("crew_app.agents._get_llm")
def test_create_archivist_agent(mock_llm):
    """create_archivist_agent が DynamoDB ツールを持つことを確認"""
    mock_llm.return_value = MagicMock()
    from crew_app.agents import create_archivist_agent
    from crew_app.tools import DynamoDBWriteTool, DynamoDBReadTool
    agent = create_archivist_agent()
    assert agent is not None
    assert agent.role == "Knowledge Archivist"
    tool_types = [type(t) for t in agent.tools]
    assert DynamoDBWriteTool in tool_types
    assert DynamoDBReadTool in tool_types
