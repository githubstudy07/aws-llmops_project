# crew_app/tools.py
"""
カスタムツール定義
- DuckDuckGoSearchTool: Web検索
- DynamoDBWriteTool: DynamoDB へのレコード保存
- DynamoDBReadTool: DynamoDB からのレコード取得

【セキュリティ原則】
boto3 クライアントは認証情報をハードコードせず、
Lambda 実行環境の IAM Role に全面的に委任する。
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from duckduckgo_search import DDGS

    class DuckDuckGoSearchTool(BaseTool):
        name: str = "DuckDuckGo Web Search"
        description: str = (
            "Web を検索して最新情報を取得するツール。"
            "引数に検索クエリ文字列を渡すこと。"
        )

        def _run(self, query: str) -> str:
            results = []
            try:
                with DDGS() as ddgs:
                    for r in ddgs.text(query, max_results=5):
                        results.append(f"- {r['title']}: {r['body']}")
                return "\n".join(results) if results else "検索結果が見つかりませんでした。"
            except Exception as e:
                return f"検索中にエラーが発生しました: {str(e)}"

except ImportError:
    DuckDuckGoSearchTool = None


# -------------------------------------------------------------------
# DynamoDB ツール用スキーマ定義
# -------------------------------------------------------------------

class DynamoDBWriteInput(BaseModel):
    content_id: str = Field(..., description="保存するレコードの一意なID")
    content: str = Field(..., description="保存するコンテンツ（調査結果・成果物等）")


class DynamoDBReadInput(BaseModel):
    content_id: str = Field(..., description="取得するレコードの一意なID")


# -------------------------------------------------------------------
# DynamoDB 書き込みツール
# -------------------------------------------------------------------

class DynamoDBWriteTool(BaseTool):
    """
    DynamoDB の WRITES_TABLE にレコードを保存するツール。
    認証は Lambda IAM Role を使用。
    """
    name: str = "DynamoDB Write Tool"
    description: str = (
        "調査結果や成果物を DynamoDB に保存するツール。"
        "content_id（一意なID文字列）と content（保存内容）を引数として渡すこと。"
    )
    args_schema: type[BaseModel] = DynamoDBWriteInput

    def _run(self, content_id: str, content: str) -> str:
        table_name = os.environ.get("WRITES_TABLE")
        if not table_name:
            return "エラー: 環境変数 WRITES_TABLE が設定されていません。"

        try:
            dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
            table = dynamodb.Table(table_name)
            table.put_item(
                Item={
                    "content_id": content_id,
                    "content": content,
                }
            )
            return f"✅ DynamoDB への保存に成功しました。content_id: {content_id}"

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            return f"❌ DynamoDB 書き込みエラー [{error_code}]: {error_msg}"

        except Exception as e:
            return f"❌ 予期しないエラー: {str(e)}"


# -------------------------------------------------------------------
# DynamoDB 読み取りツール
# -------------------------------------------------------------------

class DynamoDBReadTool(BaseTool):
    """
    DynamoDB の WRITES_TABLE からレコードを取得するツール。
    認証は Lambda IAM Role を使用。
    """
    name: str = "DynamoDB Read Tool"
    description: str = (
        "過去に保存した調査結果・成果物を DynamoDB から取得するツール。"
        "content_id（一意なID文字列）を引数として渡すこと。"
    )
    args_schema: type[BaseModel] = DynamoDBReadInput

    def _run(self, content_id: str) -> str:
        table_name = os.environ.get("WRITES_TABLE")
        if not table_name:
            return "エラー: 環境変数 WRITES_TABLE が設定されていません。"

        try:
            dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
            table = dynamodb.Table(table_name)
            response = table.get_item(Key={"content_id": content_id})

            if "Item" in response:
                item = response["Item"]
                return f"✅ 取得成功。\ncontent_id: {item['content_id']}\ncontent:\n{item['content']}"
            else:
                return f"⚠️ content_id: {content_id} のレコードは存在しません。"

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            return f"❌ DynamoDB 読み取りエラー [{error_code}]: {error_msg}"

        except Exception as e:
            return f"❌ 予期しないエラー: {str(e)}"
