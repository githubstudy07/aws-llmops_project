import json
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def env_setup():
    import os
    os.environ["AWS_REGION"] = "ap-northeast-1"

def test_lambda_handler_crew_success(env_setup):
    """CrewAI のハンドラーが正常に応答を返すかのテスト（Mock）"""
    import src.app_crew # 明示的なインポートにより属性エラーを回避
    with patch("src.app_crew.marketing_crew") as mock_crew:
        # モックの戻り値設定
        mock_result = MagicMock()
        mock_result.__str__.return_value = "Test Result Copy"
        mock_crew.kickoff.return_value = mock_result
        
        event = {
            "body": json.dumps({"target_product": "テスト商品"})
        }
        
        from src.app_crew import lambda_handler
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["result"] == "Test Result Copy"
        assert body["product"] == "テスト商品"
        
        # kickoff が呼ばれたか確認
        mock_crew.kickoff.assert_called_once_with(inputs={"target_product": "テスト商品"})
