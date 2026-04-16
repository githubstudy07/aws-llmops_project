# File: crew_app/tools.py
"""Phase 9-1: DuckDuckGo Web Search Tool for CrewAI."""

from __future__ import annotations

import logging
from typing import Any

from crewai.tools import BaseTool

logger = logging.getLogger(__name__)


class DuckDuckGoSearchTool(BaseTool):
    """DuckDuckGo search tool compatible with CrewAI v0.100+ (Pydantic v2)."""

    name: str = "duckduckgo_search"
    description: str = (
        "Searches the web using DuckDuckGo. Returns a summary of top results. "
        "Use this when you need current or real-time information. "
        "Input: a search query string."
    )
    max_results: int = 3

    def _run(self, query: str, **kwargs: Any) -> str:
        """Execute search. duckduckgo_search is imported lazily to avoid
        import errors in environments where it is mocked or unavailable.

        Args:
            query: Search query string.

        Returns:
            Formatted search results, or an informative message on failure.
        """
        # --- 遅延 import（テスト時の Mock 対応 + Lambda 環境での安全性） ---
        try:
            from duckduckgo_search import DDGS
        except ImportError as exc:
            return f"[Tool Error] duckduckgo-search package is not installed: {exc}"

        # --- 検索実行 ---
        try:
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=self.max_results))
        except Exception as exc:
            logger.warning("DuckDuckGo search failed for query '%s': %s", query, exc)
            return (
                f"[Search Error] Web search failed: {exc}. "
                "Try rephrasing the query or proceed with existing knowledge."
            )

        # --- 結果なしの場合 ---
        if not raw_results:
            return (
                f"[No Results] No results found for '{query}'. "
                "Try a different query or proceed with existing knowledge."
            )

        # --- 結果フォーマット ---
        parts: list[str] = []
        for i, r in enumerate(raw_results, 1):
            title = r.get("title", "No Title")
            href = r.get("href", "")
            body = r.get("body", "No snippet available.")
            parts.append(f"[{i}] {title}\n    URL: {href}\n    Snippet: {body}")

        return "\n\n".join(parts)
