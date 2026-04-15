# File: tests/test_crew_handler.py
import json
import pytest
from unittest.mock import MagicMock, patch

def _make_event(body: dict) -> dict:
    return {"body": json.dumps(body, ensure_ascii=False)}

class TestHandlerRouting:
    """ハンドラーの入力バリデーションとレスポンス構造のテスト"""

    def test_missing_topic_returns_400(self):
        from crew_app.app_crew import handler
        event = _make_event({})
        result = handler(event, None)
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body

    def test_valid_topic_calls_crew_kickoff(self):
        mock_result = MagicMock()
        mock_result.__str__ = lambda self: "テスト記事の内容"

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = mock_result

        with patch("crew_app.app_crew.build_crew", return_value=mock_crew):
            from crew_app.app_crew import handler
            event = _make_event({"topic": "生成AIの最新動向"})
            result = handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "result" in body
        assert body["result"] == "テスト記事の内容"

    def test_crew_exception_returns_500(self):
        mock_crew = MagicMock()
        mock_crew.kickoff.side_effect = RuntimeError("LLM timeout")

        with patch("crew_app.app_crew.build_crew", return_value=mock_crew):
            from crew_app.app_crew import handler
            event = _make_event({"topic": "テスト"})
            result = handler(event, None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "LLM timeout" in body["error"]
