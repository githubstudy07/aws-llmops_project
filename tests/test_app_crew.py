# File: tests/test_app_crew.py
import json
import pytest
from unittest.mock import MagicMock, patch

def _make_event(body: dict) -> dict:
    return {"body": json.dumps(body, ensure_ascii=False)}

class TestHandlerRouting:
    """ハンドラーの入力バリデーションとレスポンス構造のテスト"""

    def test_valid_product_calls_crew_kickoff(self):
        mock_result = MagicMock()
        mock_result.__str__ = lambda self: "テスト記事の内容"

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = mock_result

        with patch("crew_app.app_crew.build_crew", return_value=mock_crew):
            from crew_app.app_crew import handler

            event = _make_event({"target_product": "生成AIの最新動向"})
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

            event = _make_event({"target_product": "テスト"})
            result = handler(event, None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "LLM timeout" in body["error"]

class TestPysqlite3HackIsolation:
    """pysqlite3 ハックが Lambda 外では発動しないことを確認"""

    def test_lambda_task_root_not_set_in_test_env(self):
        import os
        assert "LAMBDA_TASK_ROOT" not in os.environ

    def test_sqlite3_is_importable_without_hack(self):
        import sqlite3
        import sys
        # sys.modules['sqlite3'] が差し替えられていないことを確認
        # (テスト環境では pysqlite3 はインストールされていないため KeyError または標準のが入っているはず)
        if 'pysqlite3' in sys.modules:
             # 万が一インストールされていたとしても、sqlite3 モジュールが差し替わっていないかチェック
             assert 'pysqlite3' not in sys.modules['sqlite3'].__name__
