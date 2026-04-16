# File: crew_app/tools.py
"""Phase 9-1 & 9-2: Web Search and DynamoDB Tools for CrewAI."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Type

import boto3
from botocore.exceptions import ClientError
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

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


# --------------------------------------------------------------
# DynamoDB クライアント (Lazy initialization)
# --------------------------------------------------------------
_dynamodb_resource = None


def _get_dynamodb_table():
    """DynamoDB テーブルリソースを取得する。"""
    global _dynamodb_resource
    if _dynamodb_resource is None:
        table_name = os.environ.get("ARCHIVE_TABLE", "handson-research-archives")
        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        _dynamodb_resource = dynamodb.Table(table_name)
    return _dynamodb_resource


# ==============================================================
# DynamoDBWriteTool
# ==============================================================

class DynamoDBWriteInput(BaseModel):
    """DynamoDBWriteTool の入力スキーマ"""
    content_id: str = Field(
        ...,
        description="保存するレコードの一意な識別子。例: 'research_ads_20260416'"
    )
    content: str = Field(
        ...,
        description="保存するテキストコンテンツ（調査結果、分析レポート等）"
    )


class DynamoDBWriteTool(BaseTool):
    """DynamoDB にコンテンツを書き込むツール"""

    name: str = "dynamodb_write"
    description: str = (
        "調査結果や分析レポートを DynamoDB に永続保存するツール。"
        "content_id（一意な識別子）と content（テキスト）を指定して保存する。"
    )
    args_schema: Type[BaseModel] = DynamoDBWriteInput

    def _run(self, content_id: str, content: str) -> str:
        """DynamoDB にレコードを書き込む"""
        try:
            table = _get_dynamodb_table()
            item = {
                "content_id": content_id,
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "crew_archiver",
            }
            table.put_item(Item=item)
            return f"✅ DynamoDB 書き込み成功: content_id='{content_id}'"
        except ClientError as e:
            return f"❌ DynamoDB 書き込みエラー: {e.response['Error']['Message']}"
        except Exception as e:
            return f"❌ 予期しないエラー (Write): {str(e)}"


# ==============================================================
# DynamoDBReadTool
# ==============================================================

class DynamoDBReadInput(BaseModel):
    """DynamoDBReadTool の入力スキーマ"""
    content_id: str = Field(
        ...,
        description="取得したいレコードの content_id。"
    )


class DynamoDBReadTool(BaseTool):
    """DynamoDB からコンテンツを読み取るツール"""

    name: str = "dynamodb_read"
    description: str = (
        "DynamoDB に保存済みの調査結果を content_id で取得するツール。"
    )
    args_schema: Type[BaseModel] = DynamoDBReadInput

    def _run(self, content_id: str) -> str:
        """DynamoDB からレコードを読み取る"""
        try:
            table = _get_dynamodb_table()
            response = table.get_item(Key={"content_id": content_id})

            if "Item" not in response:
                return f"⚠️ レコードが見つかりません: content_id='{content_id}'"

            item = response["Item"]
            return json.dumps(item, ensure_ascii=False, indent=2)
        except ClientError as e:
            return f"❌ DynamoDB 読み取りエラー: {e.response['Error']['Message']}"
        except Exception as e:
            return f"❌ 予期しないエラー (Read): {str(e)}"
