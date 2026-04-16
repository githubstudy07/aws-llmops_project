# File: tests/test_dynamodb_tools.py
"""
DynamoDB ツール単体テスト
前提: 環境変数 RESEARCH_ARCHIVES_TABLE に実在するテーブル名が設定されていること
      AWS 認証情報が利用可能であること（ローカルでは ~/.aws/credentials 等）
"""

import json
import os
import uuid

import pytest

# テスト対象テーブル名の設定
# デプロイ後のテーブル名を指定（未デプロイ時はスキップ）
TABLE_NAME = os.environ.get("RESEARCH_ARCHIVES_TABLE", "handson-research-archives")
os.environ["RESEARCH_ARCHIVES_TABLE"] = TABLE_NAME

from crew_app.tools import DynamoDBWriteTool, DynamoDBReadTool


@pytest.fixture
def unique_content_id():
    """テストごとに一意な content_id を生成"""
    return f"test-{uuid.uuid4().hex[:8]}"


class TestDynamoDBWriteTool:
    def test_write_success(self, unique_content_id):
        tool = DynamoDBWriteTool()
        result = tool._run(
            content_id=unique_content_id,
            content="これはテスト用のリサーチ結果です。"
        )
        assert "保存成功" in result
        assert unique_content_id in result

    def test_write_empty_content(self, unique_content_id):
        tool = DynamoDBWriteTool()
        result = tool._run(content_id=unique_content_id, content="")
        # 空文字列でも DynamoDB は受け付ける（仕様）
        assert "保存成功" in result


class TestDynamoDBReadTool:
    def test_read_existing_item(self, unique_content_id):
        # 先に書き込み
        write_tool = DynamoDBWriteTool()
        write_tool._run(
            content_id=unique_content_id,
            content="読み取りテスト用データ"
        )

        # 読み取り
        read_tool = DynamoDBReadTool()
        result = read_tool._run(content_id=unique_content_id)
        parsed = json.loads(result)
        assert parsed["content_id"] == unique_content_id
        assert parsed["content"] == "読み取りテスト用データ"
        assert "created_at" in parsed

    def test_read_nonexistent_item(self):
        read_tool = DynamoDBReadTool()
        result = read_tool._run(content_id="nonexistent-id-99999")
        assert "該当なし" in result


class TestEnvironmentVariable:
    def test_table_name_is_set(self):
        assert os.environ.get("RESEARCH_ARCHIVES_TABLE") is not None
        assert len(os.environ.get("RESEARCH_ARCHIVES_TABLE")) > 0
