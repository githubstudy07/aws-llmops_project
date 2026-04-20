import json
from unittest.mock import MagicMock, patch
import sys
import os

# Essential mocks to avoid side effects during import
sys.modules['boto3'] = MagicMock()
sys.modules['langchain_aws'] = MagicMock()
sys.modules['langchain_community.tools'] = MagicMock()
sys.modules['langgraph.prebuilt'] = MagicMock()

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

def test_lambda_handler_simple():
    from app import lambda_handler

    # Mock event
    event = {"body": json.dumps({"message": "test"})}

    # Mock the agent_executor to avoid actual LLM/tool calls
    with patch("app.agent_executor.invoke") as mock_invoke:
        mock_invoke.return_value = {
            "messages": [MagicMock(content="Restart Success")]
        }

        result = lambda_handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["status"] == "success"
        assert "Restart Success" in body["response"]
