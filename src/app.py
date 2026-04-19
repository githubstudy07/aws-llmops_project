import json
import os
import uuid
import logging
import boto3
from langchain_aws import ChatBedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from langfuse.langchain import CallbackHandler
from langchain_core.tools import tool

# Logger Setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
TABLE_NAME = os.environ.get("WRITES_TABLE", "")

# DynamoDB Setup
dynamodb = boto3.resource("dynamodb")

@tool
def archive_research_result(content: str, content_id: str = None) -> str:
    """
    Saves the final research summary or important information to DynamoDB.
    Args:
        content: The text content to save.
        content_id: Unique ID for the content (optional, will be generated if missing).
    """
    if not content_id:
        content_id = f"research-{uuid.uuid4().hex[:8]}"
    
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={
            "content_id": content_id,
            "content": content
        })
        logger.info(f"Successfully archived content with ID: {content_id}")
        return f"SUCCESS: Content archived with ID: {content_id}"
    except Exception as e:
        logger.error(f"Failed to archive to DynamoDB: {str(e)}")
        return f"ERROR: Failed to save to DynamoDB: {str(e)}"

# Define Tools
search_tool = DuckDuckGoSearchRun()
tools = [search_tool, archive_research_result]

# Langfuse Key Fetcher (SSM)
def setup_langfuse_env():
    """Retrieves Langfuse keys from SSM if not present in Environment."""
    if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY"):
        return True
    
    try:
        ssm = boto3.client("ssm")
        prefix = os.environ.get("SSM_PARAM_PREFIX", "/handson/langfuse")
        logger.info(f"Fetching Langfuse keys from SSM path: {prefix}")
        params = ssm.get_parameters_by_path(Path=prefix, WithDecryption=True)
        param_dict = {p["Name"].split("/")[-1]: p["Value"] for p in params["Parameters"]}
        
        if "public_key" in param_dict and "secret_key" in param_dict:
            os.environ["LANGFUSE_PUBLIC_KEY"] = param_dict["public_key"]
            os.environ["LANGFUSE_SECRET_KEY"] = param_dict["secret_key"]
            logger.info("Langfuse keys set from SSM.")
            return True
        else:
            logger.warning(f"Required keys (public_key, secret_key) not found in SSM at {prefix}")
    except Exception as e:
        logger.warning(f"Could not fetch Langfuse keys from SSM: {e}")
    return False

# Initialize LLM & Agent
llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    model_kwargs={"temperature": 0.1}
)
agent_executor = create_react_agent(llm, tools)

def lambda_handler(event, context):
    """
    Entry point for AWS Lambda.
    Handles user queries using a LangGraph ReAct agent.
    """
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Request parsing
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
            
        # Support both 'message' and 'topic' field names
        query = body.get("message", body.get("topic", "AI LLMOps current trends"))
        session_id = body.get("session_id", body.get("content_id", f"session-{uuid.uuid4().hex[:8]}"))

        # Setup Langfuse (Fetch keys)
        setup_langfuse_env()
        
        # Langfuse Callback Handler
        handler = CallbackHandler(
            session_id=session_id,
            user_id="aws-lambda-user"
        )
        
        # Invoke Agent
        config = {"callbacks": [handler], "recursion_limit": 10}
        inputs = {"messages": [("user", query)]}
        
        logger.info(f"Invoking LangGraph agent for session: {session_id}, query: {query}")
        response = agent_executor.invoke(inputs, config=config)
        
        # Extract last AI message content
        final_message = response["messages"][-1].content
        
        # Final Flush for Langfuse (Physical confirmation)
        handler.flush()
        logger.info("Langfuse traces flushed.")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Session-Id": session_id
            },
            "body": json.dumps({
                "status": "success",
                "session_id": session_id,
                "response": final_message
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            }, ensure_ascii=False)
        }
