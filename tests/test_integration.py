# File: tests/test_integration.py
"""Integration test: real DuckDuckGo search, no LLM.
Requires internet access. Skip in offline CI if needed.
"""

import unittest
import os
import pytest

from crew_app.tools import DuckDuckGoSearchTool


@pytest.mark.skipif(
    os.environ.get("CI_OFFLINE") == "1",
    reason="Skipping integration test in offline CI environment",
)
class TestDuckDuckGoRealSearch(unittest.TestCase):
    """Test with actual DuckDuckGo API."""

    def test_real_search_returns_results(self):
        if DuckDuckGoSearchTool is None:
            self.skipTest("DuckDuckGoSearchTool not available (import failed)")
            
        tool = DuckDuckGoSearchTool()
        result = tool._run("Python programming language")

        self.assertIsInstance(result, str)
        self.assertNotIn("エラー", result)
        # 成功メッセージまたは結果が含まれる
        self.assertTrue(len(result) > 0)

    def test_real_search_japanese(self):
        if DuckDuckGoSearchTool is None:
            self.skipTest("DuckDuckGoSearchTool not available")

        tool = DuckDuckGoSearchTool()
        result = tool._run("AWS Lambda 最新情報")

        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == "__main__":
    unittest.main()
