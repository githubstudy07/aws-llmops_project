# File: crew_app/tools.py
"""Web検索ツール定義（DuckDuckGo）"""

from __future__ import annotations

import logging
from typing import Any

from crewai.tools import BaseTool

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DuckDuckGo 検索ツール（CrewAI BaseTool 準拠）
# ---------------------------------------------------------------------------

class DuckDuckGoSearchTool(BaseTool):
    """DuckDuckGo を利用した Web 検索ツール。

    CrewAI の BaseTool を継承し、Agent が自律的に呼び出せる形式で提供する。
    Lambda 環境での実行を考慮し、タイムアウトと例外処理を内包する。
    """

    name: str = "DuckDuckGo Search Tool"
    description: str = (
        "Searches the web using DuckDuckGo and returns relevant results. "
        "Use this tool when you need to find up-to-date information on any topic. "
        "Input should be a search query string."
    )

    # 検索結果の最大取得件数
    max_results: int = 5
    # HTTP リクエストのタイムアウト（秒）
    request_timeout: int = 20

    def _run(self, query: str, **kwargs: Any) -> str:
        """検索を実行し、結果を文字列で返す。

        Args:
            query: 検索クエリ文字列

        Returns:
            検索結果のサマリー文字列。エラー時はエラーメッセージ。
        """
        if not query or not query.strip():
            return "Error: Empty search query provided."

        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            logger.error("duckduckgo-search is not installed: %s", e)
            return (
                "Error: duckduckgo-search library is not available. "
                "Please install it with: pip install duckduckgo-search"
            )

        try:
            logger.info("Searching DuckDuckGo for: %s", query)
            with DDGS() as ddgs:
                results = list(
                    ddgs.text(
                        keywords=query,
                        max_results=self.max_results,
                    )
                )

            if not results:
                logger.warning("No results found for query: %s", query)
                return f"No results found for: {query}"

            # 検索結果を構造化テキストとしてフォーマット
            formatted = []
            for i, r in enumerate(results, 1):
                title = r.get("title", "No Title")
                href = r.get("href", "")
                body = r.get("body", "")
                formatted.append(
                    f"[{i}] {title}\n    URL: {href}\n    Snippet: {body}"
                )

            output = "\n\n".join(formatted)
            logger.info(
                "DuckDuckGo search returned %d results for: %s",
                len(results),
                query,
            )
            return output

        except TimeoutError:
            logger.error("DuckDuckGo search timed out for query: %s", query)
            return f"Error: Search timed out for query: {query}"
        except Exception as e:
            logger.error(
                "DuckDuckGo search failed for query '%s': %s", query, e
            )
            return f"Error: Search failed with: {type(e).__name__}: {e}"
