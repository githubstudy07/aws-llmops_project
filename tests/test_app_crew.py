import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# src ディレクトリを sys.path に追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@patch('boto3.client')
def test_lambda_handler_crew_success(mock_boto):
    """CrewAI ロジックが正常に呼び出されるかのテスト"""
    
    # モックの設定 (import 前に行う必要がある)
    mock_ssm = MagicMock()
    mock_ssm.get_parameters_by_path.return_value = {
        "Parameters": [
            {"Name": "/handson/langfuse/public_key", "Value": "pk-123"},
            {"Name": "/handson/langfuse/secret_key", "Value": "sk-123"},
            {"Name": "/handson/langfuse/host", "Value": "http://localhost"}
        ]
    }
    mock_boto.side_effect = lambda service, **kwargs: mock_ssm if service == "ssm" else MagicMock()

    # ここで import することで、top-level の get_langfuse_config がモックされた boto3 を使う
    if 'app_crew' in sys.modules:
        del sys.modules['app_crew']
    import app_crew
    
    with patch('app_crew.create_marketing_crew') as mock_create_crew:
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
