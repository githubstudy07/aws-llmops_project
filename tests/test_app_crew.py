import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# src ディレクトリを sys.path に追加して、src. 抜きでインポート可能にする
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def env_setup():
    os.environ["AWS_REGION"] = "ap-northeast-1"

def test_lambda_handler_crew_success(env_setup):
    """CrewAI のハンドラーが正常に応答を返すかのテスト（Mock）"""
    # app_crew を直接インポート（src. 不要）
    import app_crew
    with patch("app_crew.marketing_crew") as mock_crew:
        # モックの戻り値設定
        mock_result = MagicMock()
        mock_result.__str__.return_value = "Test Result Copy"
        mock_crew.kickoff.return_value = mock_result
        
        event = {
            "body": json.dumps({"target_product": "テスト商品"})
        }
        
        response = app_crew.lambda_handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["result"] == "Test Result Copy"
        assert body["product"] == "テスト商品"
        
        # kickoff が呼ばれたか確認
        mock_crew.kickoff.assert_called_once_with(inputs={"target_product": "テスト商品"})
