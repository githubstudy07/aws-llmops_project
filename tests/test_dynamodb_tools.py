# tests/test_dynamodb_tools.py
"""
DynamoDB カスタムツールのユニットテスト
boto3 は unittest.mock でモック化し、実際の AWS 呼び出しは行わない
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

os.environ["WRITES_TABLE"] = "handson-research-archives"

from crew_app.tools import DynamoDBWriteTool, DynamoDBReadTool


class TestDynamoDBWriteTool:
    def setup_method(self):
        self.tool = DynamoDBWriteTool()

    @patch("crew_app.tools.boto3.resource")
    def test_write_success(self, mock_boto3_resource):
        """正常系: put_item が成功した場合"""
        mock_table = MagicMock()
        mock_boto3_resource.return_value.Table.return_value = mock_table

        result = self.tool._run(content_id="test-001", content="テストコンテンツ")

        mock_table.put_item.assert_called_once_with(
            Item={"content_id": "test-001", "content": "テストコンテンツ"}
        )
        assert "✅" in result
        assert "test-001" in result

    @patch("crew_app.tools.boto3.resource")
    def test_write_client_error(self, mock_boto3_resource):
        """異常系: ClientError が発生した場合"""
        mock_table = MagicMock()
        mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
            "PutItem",
        )
        mock_boto3_resource.return_value.Table.return_value = mock_table

        result = self.tool._run(content_id="test-002", content="エラーテスト")
        assert "❌" in result
        assert "ResourceNotFoundException" in result


class TestDynamoDBReadTool:
    def setup_method(self):
        self.tool = DynamoDBReadTool()

    @patch("crew_app.tools.boto3.resource")
    def test_read_success(self, mock_boto3_resource):
        """正常系: get_item が成功した場合"""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            "Item": {"content_id": "test-001", "content": "保存済みコンテンツ"}
        }
        mock_boto3_resource.return_value.Table.return_value = mock_table

        result = self.tool._run(content_id="test-001")
        assert "✅" in result
        assert "保存済みコンテンツ" in result

    @patch("crew_app.tools.boto3.resource")
    def test_read_item_not_found(self, mock_boto3_resource):
        """正常系: 対象レコードが存在しない場合"""
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}  # Item キーなし
        mock_boto3_resource.return_value.Table.return_value = mock_table

        result = self.tool._run(content_id="nonexistent-id")
        assert "⚠️" in result
        assert "nonexistent-id" in result
