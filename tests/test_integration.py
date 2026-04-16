# File: tests/test_integration.py
"""Integration test: real DuckDuckGo search, no LLM.
Requires internet access. Skip in offline CI if needed.
"""

import unittest
import os

from crew_app.tools import DuckDuckGoSearchTool


@unittest.skipIf(
    os.environ.get("CI_OFFLINE") == "1",
    "Skipping integration test in offline CI environment",
)
class TestDuckDuckGoRealSearch(unittest.TestCase):
    """Test with actual DuckDuckGo API (free, no cost)."""

    def test_real_search_returns_results(self):
        tool = DuckDuckGoSearchTool(max_results=2)
        result = tool._run("Python programming language")

        self.assertNotIn("[Tool Error]", result)
        self.assertNotIn("[Search Error]", result)
        # 通常は結果が返る
        if "[No Results]" not in result:
            self.assertIn("[1]", result)

    def test_real_search_japanese(self):
        tool = DuckDuckGoSearchTool(max_results=2)
        result = tool._run("AWS Lambda 最新情報")

        self.assertNotIn("[Tool Error]", result)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


if __name__ == "__main__":
    unittest.main()
