# File: tests/test_tools.py
"""DuckDuckGoSearchTool のユニットテスト"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from crew_app.tools import DuckDuckGoSearchTool


@pytest.fixture
def search_tool() -> DuckDuckGoSearchTool:
    return DuckDuckGoSearchTool(max_results=3, request_timeout=10)


class TestDuckDuckGoSearchToolNormal:
    """正常系テスト"""

    def test_returns_string(self, search_tool: DuckDuckGoSearchTool) -> None:
        """_run が文字列を返すことを検証"""
        mock_results = [
            {
                "title": "Test Result 1",
                "href": "https://example.com/1",
                "body": "This is test result 1.",
            },
            {
                "title": "Test Result 2",
                "href": "https://example.com/2",
                "body": "This is test result 2.",
            },
        ]

        with patch("duckduckgo_search.DDGS") as MockDDGS:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.text.return_value = iter(mock_results)
            MockDDGS.return_value = mock_instance

            result = search_tool._run(query="test query")

        assert isinstance(result, str)
        assert "Test Result 1" in result
        assert "Test Result 2" in result
        assert "https://example.com/1" in result

    def test_result_format(self, search_tool: DuckDuckGoSearchTool) -> None:
        """結果が番号付きフォーマットであることを検証"""
        mock_results = [
            {
                "title": "Title A",
                "href": "https://a.com",
                "body": "Body A",
            },
        ]

        with patch("duckduckgo_search.DDGS") as MockDDGS:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.text.return_value = iter(mock_results)
            MockDDGS.return_value = mock_instance

            result = search_tool._run(query="test")

        assert "[1]" in result


class TestDuckDuckGoSearchToolError:
    """異常系テスト"""

    def test_empty_query(self, search_tool: DuckDuckGoSearchTool) -> None:
        """空クエリ時にエラーメッセージを返すことを検証"""
        result = search_tool._run(query="")
        assert "Error" in result

    def test_whitespace_only_query(
        self, search_tool: DuckDuckGoSearchTool
    ) -> None:
        """空白のみクエリ時にエラーメッセージを返すことを検証"""
        result = search_tool._run(query="   ")
        assert "Error" in result

    def test_no_results(self, search_tool: DuckDuckGoSearchTool) -> None:
        """検索結果 0 件時のハンドリングを検証"""
        with patch("duckduckgo_search.DDGS") as MockDDGS:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.text.return_value = iter([])
            MockDDGS.return_value = mock_instance

            result = search_tool._run(query="xyznonexistent12345")

        assert "No results found" in result

    def test_network_error(self, search_tool: DuckDuckGoSearchTool) -> None:
        """ネットワークエラー時のハンドリングを検証"""
        with patch("duckduckgo_search.DDGS") as MockDDGS:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            # duckduckgo_search might raise various errors, simulating general Exception
            mock_instance.text.side_effect = Exception("Network error")
            MockDDGS.return_value = mock_instance

            result = search_tool._run(query="test")

        assert "Error" in result
        assert "Network error" in result

    def test_timeout_error(self, search_tool: DuckDuckGoSearchTool) -> None:
        """タイムアウトエラー時のハンドリングを検証"""
        with patch("duckduckgo_search.DDGS") as MockDDGS:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.text.side_effect = TimeoutError("Timed out")
            MockDDGS.return_value = mock_instance

            result = search_tool._run(query="test")

        assert "timed out" in result.lower()
