import os
import boto3
import json
from langfuse import get_client
from botocore.config import Config

# --- 1. AWS & Langfuse Configuration ---
REGION = "ap-northeast-1"
MODEL_ID = "apac.amazon.nova-micro-v1:0"
DATASET_NAME = "handson-dataset-01"
RUN_NAME = "improved-run-v1"

# Fetch Langfuse config from SSM (Reuse logic from app.py)
def get_langfuse_config():
    ssm = boto3.client("ssm", region_name=REGION)
    try:
        response = ssm.get_parameters_by_path(
            Path="/handson/langfuse/",
            WithDecryption=True
        )
        params = response.get("Parameters", [])
        config_map = {p["Name"]: p["Value"] for p in params}
        return {
            "public_key": config_map.get("/handson/langfuse/public_key"),
            "secret_key": config_map.get("/handson/langfuse/secret_key"),
            "host": config_map.get("/handson/langfuse/host")
        }
    except Exception as e:
        print(f"Error fetching SSM config: {e}")
        return None

config_data = get_langfuse_config()
if not config_data:
    raise Exception("Could not fetch Langfuse config. Check AWS credentials.")

os.environ["LANGFUSE_PUBLIC_KEY"] = config_data["public_key"]
os.environ["LANGFUSE_SECRET_KEY"] = config_data["secret_key"]
os.environ["LANGFUSE_HOST"] = config_data["host"]

langfuse = get_client()
bedrock_client = boto3.client("bedrock-runtime", region_name=REGION, config=Config(read_timeout=300))

# --- 2. Define the Task Function ---
def chatbot_task(item):
    """
    Executes the LLM inference for a given dataset item.
    Expects item['input'] to contain the user message.
    """
    # Langfuse Dataset items often have 'input' as a dict or string
    # Based on our previous Trace, it was wrapped in {"messages": [...]} 
    # but the 'Add to dataset' screen showed it as a dict.
    
    user_input = item.input
    if isinstance(user_input, dict) and "messages" in user_input:
        # Extract last message content if it matches our app's structure
        messages = user_input["messages"]
        prompt_text = messages[-1]["content"] if isinstance(messages[-1], dict) else messages[-1].content
    else:
        # Fallback for simple string inputs
        prompt_text = str(user_input)

    # 修正: プロンプトの改善（専門家設定と回答方針の具体化）
    system_prompt = "あなたは AWS LLMOps の専門家です。ユーザーの質問に対して、技術的に正確かつ、初心者にも分かりやすく構成図を想起させるような丁寧な回答を心がけてください。"
    input_data = {
        "system": system_prompt,
        "messages": [{"role": "user", "content": [{"text": prompt_text}]}]
    }

    # run_experiment の中での明示的な Generation 記録
    with langfuse.start_as_current_observation(
        as_type="generation",
        name="bedrock-generation-experiment",
        model=MODEL_ID,
        input=input_data,
        model_parameters={"temperature": 0.7, "maxTokens": 300}
    ) as generation:
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=input_data["messages"],
            system=[{"text": system_prompt}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.7}
        )
        
        output_text = response["output"]["message"]["content"][0]["text"]
        
        # 結果を記録
        generation.update(output=output_text)
        return output_text

# --- 3. Run Experiment ---
def main():
    print(f"Starting Experiment: {RUN_NAME} on dataset: {DATASET_NAME}")
    
    try:
        dataset = langfuse.get_dataset(DATASET_NAME)
        
        # Use run_experiment (SDK v3/v4 recommended)
        # This will iterate through all items, call chatbot_task, and log to Langfuse
        dataset.run_experiment(
            name=RUN_NAME,
            task=chatbot_task,
            description="Baseline run with current system prompt.",
            # Optional: integration metadata
            metadata={
                "model": MODEL_ID,
                "environment": "local-experiment"
            }
        )
        
        langfuse.flush()
        print("\nExperiment completed successfully!")
        print(f"Check results at: {config_data['host']}/datasets/{DATASET_NAME}")
        
    except Exception as e:
        print(f"Experiment failed: {e}")

if __name__ == "__main__":
    main()
