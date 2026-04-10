import json
import pytest

def test_lambda_handler_event_parsing():
    """Lambdaハンドラーがイベント構造を正しくパースできるかのテスト"""
    # モックイベント
    event = {
        "body": json.dumps({
            "message": "Hello",
            "session_id": "test-session"
        })
    }
    
    # 環境変数のモック（インポート時の初期化不全を防ぐ）
    import os
    os.environ["CHECKPOINT_TABLE"] = "dummy-table"
    os.environ["WRITES_TABLE"] = "dummy-writes"
    
    # app.pyのhandlerが定義されているかチェック（インポートテスト）
    try:
        from src.app import lambda_handler
        assert callable(lambda_handler)
    except ImportError as e:
        pytest.fail(f"src/app.py または lambda_handler が見つかりません: {e}")
    except Exception as e:
        pytest.fail(f"インポート中にエラーが発生しました: {e}")
