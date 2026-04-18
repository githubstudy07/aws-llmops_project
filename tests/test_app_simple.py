import json
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Essential mocks to avoid side effects during import
sys.modules['boto3'] = MagicMock()
sys.modules['langfuse'] = MagicMock()
sys.modules['langfuse.langchain'] = MagicMock()
sys.modules['langchain_aws'] = MagicMock()
sys.modules['langchain_community.tools'] = MagicMock()
sys.modules['langchain_core.tools'] = MagicMock()
sys.modules['langgraph'] = MagicMock()
sys.modules['langgraph.prebuilt'] = MagicMock()

# Add src to sys.path for testing
sys.path.append(os.path.join(os.getcwd(), 'src'))

def _make_event(body: dict) -> dict:
    return {"body": json.dumps(body, ensure_ascii=False)}

class TestLangGraphHandler:
    @patch("app.agent_executor.invoke")
    @patch("app.setup_langfuse_env")
    @patch("app.CallbackHandler")
    def test_handler_basic(self, mock_cb, mock_env, mock_invoke):
        from app import lambda_handler
        
        # Mocking the graph execution
        mock_invoke.return_value = {
            "messages": [MagicMock(content="Mocked answer")]
        }
        
        event = _make_event({"topic": "test topic"})
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["status"] == "success"
        assert "Mocked answer" in body["response"]

    def test_handler_error(self):
        from app import lambda_handler
        with patch("app.agent_executor.invoke", side_effect=Exception("API Error")):
            event = _make_event({"topic": "test"})
            result = lambda_handler(event, None)
            
            assert result["statusCode"] == 500
            body = json.loads(result["body"])
            assert body["status"] == "error"
            assert "API Error" in body["message"]
