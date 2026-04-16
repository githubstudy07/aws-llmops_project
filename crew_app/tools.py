# File: crew_app/tools.py
"""
CrewAI カスタムツール定義
Phase 9-2: DynamoDB Write/Read ツールを追加
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Type

import boto3
from botocore.exceptions import ClientError
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================================
# DynamoDB ヘルパー
# ============================================================

def _get_dynamodb_table():
    """
    環境変数 RESEARCH_ARCHIVES_TABLE からテーブル名を取得し、
    boto3 Table リソースを返す。
    認証情報は Lambda 実行ロールの IAM Role に委任（ハードコード禁止）。
    """
    table_name = os.environ.get("RESEARCH_ARCHIVES_TABLE")
    if not table_name:
        raise ValueError(
            "環境変数 RESEARCH_ARCHIVES_TABLE が設定されていません。"
            "template.yaml の Environment.Variables を確認してください。"
        )
    dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
    return dynamodb.Table(table_name)


# ============================================================
# DynamoDB Write Tool
# ============================================================

class DynamoDBWriteInput(BaseModel):
    """DynamoDBWriteTool の入力スキーマ"""
    content_id: str = Field(
        description="保存するコンテンツの一意な識別子（例: 'research-20260416-001'）"
    )
    content: str = Field(
        description="保存するコンテンツ本文（リサーチ結果、レポート等）"
    )


class DynamoDBWriteTool(BaseTool):
    """リサーチ結果やレポートを DynamoDB に保存するツール"""
    name: str = "dynamodb_write"
    description: str = (
        "リサーチ結果やレポートを DynamoDB に保存する。"
        "content_id（一意な識別子）と content（本文）を指定して使用する。"
        "保存が成功した場合は成功メッセージ、失敗した場合はエラー内容を返す。"
    )
    args_schema: Type[BaseModel] = DynamoDBWriteInput

    def _run(self, content_id: str, content: str) -> str:
        try:
            table = _get_dynamodb_table()
            item = {
                "content_id": content_id,
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source": "crewai-archivist",
            }
            table.put_item(Item=item)
            logger.info(f"DynamoDB 書き込み成功: content_id={content_id}")
            return f"保存成功: content_id='{content_id}' を DynamoDB に保存しました。"
        except ClientError as e:
            error_msg = e.response["Error"]["Message"]
            logger.error(f"DynamoDB 書き込み失敗: {error_msg}")
            return f"保存失敗: {error_msg}"
        except Exception as e:
            logger.error(f"DynamoDB 書き込み例外: {e}")
            return f"保存失敗: {str(e)}"


# ============================================================
# DynamoDB Read Tool
# ============================================================

class DynamoDBReadInput(BaseModel):
    """DynamoDBReadTool の入力スキーマ"""
    content_id: str = Field(
        description="取得したいコンテンツの識別子（例: 'research-20260416-001'）"
    )


class DynamoDBReadTool(BaseTool):
    """DynamoDB から過去のリサーチ結果やレポートを取得するツール"""
    name: str = "dynamodb_read"
    description: str = (
        "DynamoDB から過去のリサーチ結果やレポートを取得する。"
        "content_id を指定して、保存済みのコンテンツを読み取る。"
        "該当データがあればその内容を、なければ未検出メッセージを返す。"
    )
    args_schema: Type[BaseModel] = DynamoDBReadInput

    def _run(self, content_id: str) -> str:
        try:
            table = _get_dynamodb_table()
            response = table.get_item(Key={"content_id": content_id})
            item = response.get("Item")
            if item:
                logger.info(f"DynamoDB 読み取り成功: content_id={content_id}")
                return json.dumps(item, ensure_ascii=False, default=str)
            else:
                logger.info(f"DynamoDB レコード未検出: content_id={content_id}")
                return f"該当なし: content_id='{content_id}' のレコードは見つかりませんでした。"
        except ClientError as e:
            error_msg = e.response["Error"]["Message"]
            logger.error(f"DynamoDB 読み取り失敗: {error_msg}")
            return f"読み取り失敗: {error_msg}"
        except Exception as e:
            logger.error(f"DynamoDB 読み取り例外: {e}")
            return f"読み取り失敗: {str(e)}"
