import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# src ディレクトリを sys.path に追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


@pytest.fixture
def env_setup():
    os.environ["AWS_REGION"] = "ap-northeast-1"


def test_lambda_handler_crew_success(env_setup):
    """CrewAI のハンドラーが正常に応答を返すかのテスト（Mock）"""

    # ★ create_marketing_crew を丸ごとモック化することで
    # LLM の初期化を完全に回避します
    with patch("app_crew.create_marketing_crew") as mock_factory:
        # モックの Crew オブジェクトを設定
        mock_crew = MagicMock()
        mock_result = MagicMock()
        mock_result.__str__.return_value = "Test Result Copy"
        mock_crew.kickoff.return_value = mock_result
        mock_factory.return_value = mock_crew

        import app_crew
        event = {
            "body": json.dumps({"target_product": "テスト商品"})
        }

        response = app_crew.lambda_handler(event, None)

        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        assert body["result"] == "Test Result Copy"
        assert body["product"] == "テスト商品"

        # create_marketing_crew が呼ばれ、kickoff が実行されたか確認
        mock_factory.assert_called_once()
        mock_crew.kickoff.assert_called_once_with(inputs={"target_product": "テスト商品"})
