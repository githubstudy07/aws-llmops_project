import json
import os
import logging
import boto3
from langchain_aws import ChatBedrock
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent

# Logger Setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")

def get_agent():
    """Lazy initialization of the agent to avoid import-time side effects."""
    llm = ChatBedrock(
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={"temperature": 0.1}
    )
    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    
    return create_react_agent(llm, tools)

def lambda_handler(event, context):
    """
    Minimal LangGraph Handler for AWS Lambda (Restart Version).
    """
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Request parsing
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
            
        query = body.get("message", "What are the latest trends in AWS LLMOps 2026?")
        
        # Initialize Agent
        agent = get_agent()
        
        # Invoke Agent
        inputs = {"messages": [("user", query)]}
        logger.info(f"Invoking LangGraph agent with query: {query}")
        
        response = agent.invoke(inputs)
        
        # Extract last AI message content
        final_message = response["messages"][-1].content
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "success",
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
