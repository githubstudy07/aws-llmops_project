import json
import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# src ディレクトリを sys.path に追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

def test_lambda_handler_diagnostic_success():
    """診断モードのハンドラーが正常に応答を返すかのテスト"""
    import app_crew
    # モックなしで実行（ローカル環境にライブラリがなくても try-except で status: 200 になるはず）
    event = {
        "body": json.dumps({"test": "data"})
    }

    response = app_crew.lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "diagnostic_mode"
    assert "diagnostics" in body
    assert "python_version" in body
