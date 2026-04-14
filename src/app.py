import json
import os
import boto3
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph_checkpoint_dynamodb.saver import DynamoDBSaver
from botocore.config import Config

# 環境変数
REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
CHECKPOINT_TABLE = os.environ.get("CHECKPOINT_TABLE")
WRITES_TABLE = os.environ.get("WRITES_TABLE")

# Bedrock Runtime クライアント
config = Config(read_timeout=300, retries={'max_attempts': 3})
client = boto3.client("bedrock-runtime", region_name=REGION, config=config)

# Langfuse 設定の取得 (SSM Parameter Store)
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
        print(f"Warning: Failed to fetch Langfuse config from SSM: {e}")
        return None

LANGFUSE_CONF = get_langfuse_config()

# SDK インポートと環境変数セット
IMPORT_ERR = "None"
try:
    from langfuse.langchain import CallbackHandler
    from langfuse import get_client
except ImportError as e:
    IMPORT_ERR = str(e)
    CallbackHandler = None
    get_client = None

if LANGFUSE_CONF and LANGFUSE_CONF.get("secret_key"):
    os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_CONF["public_key"]
    os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_CONF["secret_key"]
    os.environ["LANGFUSE_HOST"] = LANGFUSE_CONF["host"]

# 5. クライアントの初期化
langfuse_client = None
if LANGFUSE_CONF and get_client:
    try:
        langfuse_client = get_client(
            public_key=LANGFUSE_CONF["public_key"],
            secret_key=LANGFUSE_CONF["secret_key"],
            host=LANGFUSE_CONF["host"]
        )
    except Exception as e:
        print(f"Error: Failed to initialize Langfuse client: {e}")

# 1. State (状態) の定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義
def chatbot(state: State, config: dict = None):
    if config is None: config = {}
    
    bedrock_messages = []
    for msg in state["messages"]:
        m_type = getattr(msg, "type", "") if not isinstance(msg, dict) else msg.get("type", msg.get("role", ""))
        role = "user" if m_type in ["human", "user"] else "assistant"
        m_content = getattr(msg, "content", "") if not isinstance(msg, dict) else msg.get("content", "")
        bedrock_messages.append({"role": role, "content": [{"text": m_content}]})

    # 2. システムプロンプトの取得 (Langfuse または 従来のハードコード)
    default_system_prompt = "あなたはAIアシスタントです。現在は[FALLBACK]モードで動作しています。回答の冒頭に【FALLBACK】と付けてください。"
    system_prompt = default_system_prompt
    prompt_tag = "fallback"

    if langfuse_client:
        try:
            # Langfuse から対象のプロンプトを取得 (ラベル 'Production' を指定)
            # 理由: Langfuse のラベルはケースセンシティブであり、画面上の表示に合わせるため
            langfuse_prompt = langfuse_client.get_prompt(
                "main-chatbot-prompt", 
                label="Production", 
                cache_ttl_seconds=0  # テストのため一時的にキャッシュ無効化
            )
            system_prompt = langfuse_prompt.compile()
            prompt_tag = f"langfuse (v{langfuse_prompt.version})"
        except Exception as e:
            print(f"Warning: Failed to fetch prompt from Langfuse, using default: {e}")
            prompt_tag = f"fallback (error: {str(e)[:50]})"

    # [Option A] コスト管理 & トレーシング
    if langfuse_client:
        try:
            # システムプロンプトも含めた入力データを構築（UIでの観測性向上のため）
            input_data = {
                "system": system_prompt,
                "messages": bedrock_messages
            }

            # コンテキストマネージャーにより自動で親子関係と属性が維持される
            with langfuse_client.start_as_current_observation(
                as_type="generation",
                name="bedrock-generation",
                model=MODEL_ID,
                input=input_data,
                model_parameters={"temperature": 0.7, "maxTokens": 300},
                metadata={"prompt_source": prompt_tag}
            ) as generation:
                response = client.converse(
                    modelId=MODEL_ID,
                    messages=bedrock_messages,
                    system=[{"text": system_prompt}],
                    inferenceConfig={"maxTokens": 300, "temperature": 0.7}
                )
                usage = response.get("usage", {})
                output_text = response["output"]["message"]["content"][0]["text"]

                # トークン使用量を連携 (コスト自動計算のトリガー)
                generation.update(
                    output=output_text,
                    usage_details={
                        "input_tokens": usage.get("inputTokens", 0),
                        "output_tokens": usage.get("outputTokens", 0),
                        "total_tokens": usage.get("totalTokens", 0)
                    }
                )
                return {"messages": [{"role": "assistant", "content": output_text, "metadata": {"prompt_source": prompt_tag}}]}
        except Exception as e:
            print(f"Warning: Langfuse tracking failed, but continuing: {e}")

    # フォールバック (Langfuse 不在時または例外発生時)
    response = client.converse(
        modelId=MODEL_ID,
        messages=bedrock_messages,
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": 300, "temperature": 0.7}
    )
    return {"messages": [{"role": "assistant", "content": response["output"]["message"]["content"][0]["text"], "metadata": {"prompt_source": prompt_tag}}]}

# 3. グラフの構築
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

checkpointer = DynamoDBSaver(
    checkpoints_table_name=CHECKPOINT_TABLE,
    writes_table_name=WRITES_TABLE,
    client_config={"region_name": REGION}
)
app = workflow.compile(checkpointer=checkpointer)

def lambda_handler(event, context):
    INIT_ERR = "None"
    try:
        path = event.get("resource", "/chat")
        body = json.loads(event.get("body", "{}"))

        if path == "/feedback":
            trace_id = body.get("trace_id")
            score_value = body.get("score_value")
            
            if not trace_id or score_value is None:
                return {"statusCode": 400, "body": json.dumps({"error": "trace_id and score_value are required"})}
                
            if langfuse_client:
                langfuse_client.create_score(
                    trace_id=trace_id,
                    name=body.get("score_name", "user-feedback"),
                    value=score_value,
                    comment=body.get("comment", "")
                )
                langfuse_client.flush()
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"status": "success", "message": "Score recorded"})
                }
            else:
                return {"statusCode": 500, "body": json.dumps({"error": "Langfuse client not initialized"})}

        # /chat endpoint handling
        user_input = body.get("message")
        thread_id = body.get("session_id", "default-session")

        if not user_input:
            return {"statusCode": 400, "body": json.dumps({"error": "Message is required"})}

        callbacks = []
        handler = None
        if CallbackHandler and langfuse_client:
            try:
                # 修正: セッション ID は metadata を通じて渡す
                handler = CallbackHandler()
                callbacks.append(handler)
            except Exception as e:
                INIT_ERR = str(e)

        graph_config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": callbacks,
            "metadata": {
                "langfuse_session_id": thread_id, # SDK v3+ 推奨形式
                "user_input": user_input
            }
        }
        
        output = app.invoke({"messages": [{"role": "user", "content": user_input}]}, graph_config)

        if langfuse_client:
            langfuse_client.flush()
        
        last_msg = output["messages"][-1]
        response_text = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", str(last_msg))

        # 3. メタデータの最終抽出
        # chatbot ノードが返却した {"messages": [{"metadata": {...}}]} を確実に拾う
        prompt_source_info = "unknown"
        if isinstance(last_msg, dict):
            prompt_source_info = last_msg.get("metadata", {}).get("prompt_source", "unknown_nested_metadata")
            if prompt_source_info == "unknown_nested_metadata":
                prompt_source_info = last_msg.get("prompt_source", "unknown_dict_root")
        elif hasattr(last_msg, "response_metadata"):
            prompt_source_info = last_msg.response_metadata.get("prompt_source", "unknown_response_metadata")
        elif hasattr(last_msg, "additional_kwargs"):
            prompt_source_info = last_msg.additional_kwargs.get("metadata", {}).get("prompt_source", 
                                  last_msg.additional_kwargs.get("prompt_source", "unknown_additional_kwargs"))

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "response": response_text,
                "session_id": thread_id,
                "trace_id": trace_id,
                "prompt_source": prompt_source_info
            }, ensure_ascii=False)
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
