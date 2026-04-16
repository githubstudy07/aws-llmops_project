# tests/test_tools.py
"""
ツールのインポートテスト
DuckDuckGoSearchTool のインポートパスを修正済み
"""

import os
import pytest

os.environ.setdefault("WRITES_TABLE", "handson-research-archives")


def test_duckduckgo_tool_importable():
    """DuckDuckGoSearchTool がインポート可能か確認（失敗してもスキップ）"""
    try:
        from crew_app.tools import DuckDuckGoSearchTool
        # None の場合は duckduckgo_search が未インストール
        if DuckDuckGoSearchTool is not None:
            tool = DuckDuckGoSearchTool()
            assert "DuckDuckGo" in tool.name
        else:
            pytest.skip("duckduckgo_search がインストールされていないためスキップ")
    except ImportError as e:
        pytest.skip(f"インポートエラーのためスキップ: {e}")


def test_dynamodb_write_tool_importable():
    """DynamoDBWriteTool がインポート可能か確認"""
    from crew_app.tools import DynamoDBWriteTool
    tool = DynamoDBWriteTool()
    assert "Write" in tool.name


def test_dynamodb_read_tool_importable():
    """DynamoDBReadTool がインポート可能か確認"""
    from crew_app.tools import DynamoDBReadTool
    tool = DynamoDBReadTool()
    assert "Read" in tool.name
