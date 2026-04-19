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
    
    with patch("app.get_agent") as mock_agent_factory:
        mock_agent = MagicMock()
        mock_agent.invoke.return_value = {
            "messages": [MagicMock(content="Restart Success")]
        }
        mock_agent_factory.return_value = mock_agent
        
        result = lambda_handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["status"] == "success"
        assert "Restart Success" in body["response"]
