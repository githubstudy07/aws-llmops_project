import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# src ディレクトリを sys.path に追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@patch('app_crew.get_langfuse_config')
@patch('app_crew.create_marketing_crew')
@patch('boto3.client')
def test_lambda_handler_crew_success(mock_boto, mock_create_crew, mock_get_config):
    """CrewAI ロジックが正常に呼び出されるかのテスト"""
    import app_crew
    
    # モックの設定
    mock_get_config.return_value = {
        "public_key": "pk-123",
        "secret_key": "sk-123",
        "host": "http://localhost"
    }
    
    mock_crew = MagicMock()
    mock_crew.kickoff.return_value = "AI Marketing Result"
    mock_create_crew.return_value = mock_crew
    
    event = {
        "body": json.dumps({"message": "Robot Vacuum"})
    }
    
    response = app_crew.lambda_handler(event, None)
    
    # 検証
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "success"
    assert "Robot Vacuum" in body["target_product"]
    assert "AI Marketing Result" in body["response"]
    
    # 呼び出し確認
    mock_create_crew.assert_called_once()
    mock_crew.kickoff.assert_called_once_with(inputs={'target_product': 'Robot Vacuum'})
