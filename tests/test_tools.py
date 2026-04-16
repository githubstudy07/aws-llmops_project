# File: tests/test_tools.py
"""Unit tests for DuckDuckGoSearchTool.

All external dependencies (duckduckgo_search) are mocked.
No network calls, no LLM calls, no cost.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestDuckDuckGoSearchToolMetadata(unittest.TestCase):
    """Test tool instantiation and metadata."""

    def test_instantiation_and_fields(self):
        from crew_app.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool()
        self.assertEqual(tool.name, "duckduckgo_search")
        self.assertIn("DuckDuckGo", tool.description)
        self.assertEqual(tool.max_results, 3)


class TestDuckDuckGoSearchToolNormal(unittest.TestCase):
    """Test _run method with mocked search results."""

    @patch("duckduckgo_search.DDGS", autospec=False)
    def test_returns_formatted_results(self, mock_ddgs_cls):
        """Normal case: search returns 2 results."""
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.text.return_value = [
            {"title": "Title A", "href": "https://example.com/a", "body": "Snippet A"},
            {"title": "Title B", "href": "https://example.com/b", "body": "Snippet B"},
        ]
        mock_ddgs_cls.return_value = mock_instance

        from crew_app.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool(max_results=2)
        result = tool._run("test query")

        self.assertIn("[1] Title A", result)
        self.assertIn("[2] Title B", result)
        self.assertIn("https://example.com/a", result)
        mock_instance.text.assert_called_once_with("test query", max_results=2)

    @patch("duckduckgo_search.DDGS", autospec=False)
    def test_returns_string_type(self, mock_ddgs_cls):
        """Verify return type is always str."""
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.text.return_value = [
            {"title": "T", "href": "https://x.com", "body": "B"},
        ]
        mock_ddgs_cls.return_value = mock_instance

        from crew_app.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool()
        result = tool._run("anything")
        self.assertIsInstance(result, str)


class TestDuckDuckGoSearchToolEdgeCases(unittest.TestCase):
    """Test error and edge cases."""

    @patch("duckduckgo_search.DDGS", autospec=False)
    def test_no_results(self, mock_ddgs_cls):
        """Edge case: search returns empty list."""
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.text.return_value = []
        mock_ddgs_cls.return_value = mock_instance

        from crew_app.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool()
        result = tool._run("nonexistent topic xyz")

        self.assertIn("[No Results]", result)

    @patch("duckduckgo_search.DDGS", autospec=False)
    def test_search_exception(self, mock_ddgs_cls):
        """Error case: DuckDuckGo raises an exception."""
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.text.side_effect = Exception("Rate limited")
        mock_ddgs_cls.return_value = mock_instance

        from crew_app.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool()
        result = tool._run("failing query")

        self.assertIn("[Search Error]", result)
        self.assertIn("Rate limited", result)

    @patch("duckduckgo_search.DDGS", autospec=False)
    def test_timeout_exception(self, mock_ddgs_cls):
        """Error case: search times out."""
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.text.side_effect = TimeoutError("Connection timed out")
        mock_ddgs_cls.return_value = mock_instance

        from crew_app.tools import DuckDuckGoSearchTool

        tool = DuckDuckGoSearchTool()
        result = tool._run("timeout query")

        self.assertIn("[Search Error]", result)


if __name__ == "__main__":
    unittest.main()
