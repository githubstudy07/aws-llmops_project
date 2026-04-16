# File: tests/test_crew_handler.py
import json
import pytest
from unittest.mock import MagicMock, patch

def _make_event(body: dict) -> dict:
    return {"body": json.dumps(body, ensure_ascii=False)}

class TestHandlerRouting:
    """ハンドラーの入力バリデーションとレスポンス構造のテスト"""

    def test_default_topic_returns_200(self):
        """topic が空でもデフォルト値を使用して 200 を返すことを確認"""
        # Crew.kickoff をモック化して LLM 呼び出しを回避
        with patch("crew_app.app_crew.Crew.kickoff", return_value="success"):
            from crew_app.app_crew import lambda_handler
            event = _make_event({})
            result = lambda_handler(event, None)
            assert result["statusCode"] == 200
            body = json.loads(result["body"])
            assert body["status"] == "success"
            assert body["topic"] == "AIエージェント最新動向"

    def test_valid_topic_calls_crew_kickoff(self):
        """有効な topic で Crew が実行されることを確認"""
        mock_result = "テスト成果物"

        with patch("crew_app.app_crew.Crew.kickoff", return_value=mock_result):
            from crew_app.app_crew import lambda_handler
            event = _make_event({"topic": "生成AIの最新動向"})
            result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "result" in body
        assert body["result"] == mock_result

    def test_crew_exception_returns_500(self):
        """例外発生時に 500 エラーを返すことを確認"""
        with patch("crew_app.app_crew.Crew.kickoff", side_effect=Exception("Execution failed")):
            from crew_app.app_crew import lambda_handler
            event = _make_event({"topic": "テスト"})
            result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "message" in body
        assert "Execution failed" in body["message"]
