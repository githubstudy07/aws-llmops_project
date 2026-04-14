import json
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def env_setup():
    import os
    os.environ["CHECKPOINT_TABLE"] = "dummy-table"
    os.environ["WRITES_TABLE"] = "dummy-writes"
    os.environ["AWS_REGION"] = "ap-northeast-1"

def test_lambda_handler_chat_route(env_setup):
    """/chat エンドポイントが trace_id を返却するかのテスト"""
    with patch("src.app.app.invoke") as mock_invoke, \
         patch("src.app.CallbackHandler") as mock_cb_class, \
         patch("src.app.langfuse_client") as mock_lf:
        
        # モックの設定
        mock_invoke.return_value = {
            "messages": [
                {"role": "assistant", "content": "Hello assistant", "prompt_source": "mock_source"}
            ]
        }
        mock_handler = MagicMock()
        mock_cb_class.return_value = mock_handler
        # CallbackHandler が正常にインスタンス化された体にする
        mock_cb_class.side_effect = lambda: mock_handler 
        
        mock_handler.last_trace_id = "test-trace-id-123"
        
        event = {
            "resource": "/chat",
            "body": json.dumps({"message": "Hello", "session_id": "session-123"})
        }
        
        from src.app import lambda_handler
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "trace_id" in body
        assert "response" in body

def test_lambda_handler_feedback_route(env_setup):
    """/feedback エンドポイントが正しくスコアを送信するかのテスト"""
    with patch("src.app.langfuse_client") as mock_lf:
        event = {
            "resource": "/feedback",
            "body": json.dumps({
                "trace_id": "test-trace-id-456",
                "score_value": 1,
                "score_name": "user-feedback",
                "comment": "Good job"
            })
        }
        
        from src.app import lambda_handler
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["status"] == "success"
        
        # Langfuse client が呼ばれたか
        mock_lf.create_score.assert_called_once_with(
            trace_id="test-trace-id-456",
            name="user-feedback",
            value=1,
            comment="Good job"
        )
        mock_lf.flush.assert_called_once()

def test_lambda_handler_feedback_invalid_params(env_setup):
    """/feedback エンドポイントのバリデーションテスト"""
    event = {
        "resource": "/feedback",
        "body": json.dumps({"trace_id": "test-trace-id-456"}) # score_value 欠落
    }
    
    from src.app import lambda_handler
    response = lambda_handler(event, None)
    
    assert response["statusCode"] == 400
    assert "required" in response["body"]
