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
SSM_ERR = "None"
SSM_NAMES = []
INIT_ERR = "None"
def get_langfuse_config():
    global SSM_ERR, SSM_NAMES
    ssm = boto3.client("ssm", region_name=REGION)
    try:
        # パラメータを一括取得
        response = ssm.get_parameters_by_path(
            Path="/handson/langfuse/",
            WithDecryption=True
        )
        params = response.get("Parameters", [])
        SSM_NAMES = [p["Name"] for p in params]
        
        config_map = {p["Name"]: p["Value"] for p in params}
        return {
            "public_key": config_map.get("/handson/langfuse/public_key"),
            "secret_key": config_map.get("/handson/langfuse/secret_key"),
            "host": config_map.get("/handson/langfuse/host")
        }
    except Exception as e:
        SSM_ERR = str(e)
        print(f"Warning: Failed to fetch Langfuse config from SSM: {e}")
        return None

LANGFUSE_CONF = get_langfuse_config()
IMPORT_ERR = "None"
try:
    import langfuse
    # 全力で CallbackHandler を探す
    found_path = "Not Found"
    import os
    for root, dirs, files in os.walk("/var/task/langfuse"):
        if "callback.py" in files:
            found_path = os.path.join(root, "callback.py")
            break
        if "callback" in dirs:
            found_path = os.path.join(root, "callback")
            break
    
    # 見つかったパスから推測してインポートを試みる
    if "langchain" in found_path:
        from langfuse.langchain.callback import CallbackHandler
    elif "callback" in found_path:
        from langfuse.callback import CallbackHandler
    else:
        from langfuse.callback import CallbackHandler # Default fallback
        
    from langfuse import Langfuse
except Exception as ie:
    IMPORT_ERR = f"{str(ie)} | FoundPath={found_path}"
    class CallbackHandler:
        def __init__(self, *args, **kwargs):
            self.langfuse = Langfuse()
            self.raise_error = False
        def flush(self): pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    class Langfuse:
        def __init__(self, *args, **kwargs): pass
        def generation(self, *args, **kwargs):
            class MockGen:
                def end(self, *args, **kwargs): pass
            return MockGen()

# Langfuse クライアントの初期化 (単体操作用)
langfuse_client = None
if LANGFUSE_CONF and LANGFUSE_CONF.get("secret_key"):
    try:
        langfuse_client = Langfuse(
            public_key=LANGFUSE_CONF["public_key"],
            secret_key=LANGFUSE_CONF["secret_key"],
            host=LANGFUSE_CONF["host"]
        )
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse client: {e}")

# 1. State (状態) の定義
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義: AI を呼び出す関数
def chatbot(state: State, config: dict = None):
    # config が渡されない場合のガード
    if config is None:
        config = {}
    # Langfuse ハンドラーの取得 (追跡コンテキストの継承)
    callbacks = config.get("callbacks", [])
    handler = next((c for c in callbacks if isinstance(c, CallbackHandler)), None)

    bedrock_messages = []
    for msg in state["messages"]:
        # オブジェクト型と辞書型の両方に対応
        m_type = getattr(msg, "type", "") if not isinstance(msg, dict) else msg.get("type", msg.get("role", ""))
        role = "user" if m_type in ["human", "user"] else "assistant"
        
        m_content = getattr(msg, "content", "") if not isinstance(msg, dict) else msg.get("content", "")
        
        bedrock_messages.append({
            "role": role,
            "content": [{"text": m_content}]
        })

    # Generation (生成) の記録開始
    generation = None
    if handler and hasattr(handler, "langfuse"):
        try:
            generation = handler.langfuse.generation(
                name="bedrock-generation",
                model=MODEL_ID,
                model_parameters={"temperature": 0.7, "maxTokens": 300},
                input=bedrock_messages
            )
        except Exception as ge:
            print(f"Warning: Failed to create Langfuse generation: {ge}")

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=bedrock_messages,
            system=[{"text": "あなたは簡潔に回答する、親切な AI アシスタントです。"}],
            inferenceConfig={"maxTokens": 300, "temperature": 0.7}
        )
        usage = response.get("usage", {})
        output_text = response["output"]["message"]["content"][0]["text"]

        # 成功時の記録
        if generation:
            try:
                generation.end(
                    output=output_text,
                    usage={
                        "input": usage.get("inputTokens", 0),
                        "output": usage.get("outputTokens", 0),
                        "total": usage.get("totalTokens", 0)
                    }
                )
            except Exception as ee:
                print(f"Warning: Failed to end Langfuse generation: {ee}")

        return {"messages": [{"role": "assistant", "content": output_text}]}
    except Exception as e:
        if generation:
            generation.end(level="ERROR", status_message=str(e))
        print(f"Error invoking Bedrock: {e}")
        return {"messages": [{"role": "assistant", "content": f"エラーが発生しました。"}]}

# 3. グラフの構築
workflow = StateGraph(State)
workflow.add_node("chatbot", chatbot)
workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 4. DynamoDB チェックポインターの設定
checkpointer = DynamoDBSaver(
    checkpoints_table_name=CHECKPOINT_TABLE,
    writes_table_name=WRITES_TABLE,
    client_config={"region_name": REGION}
)

# コンパイル
app = workflow.compile(checkpointer=checkpointer)

def lambda_handler(event, context):
    """
    API Gateway からのリクエストを処理する Lambda ハンドラー
    """
    try:
        # リクエストボディの解析
        body = json.loads(event.get("body", "{}"))
        user_input = body.get("message")
        thread_id = body.get("session_id", "default-session")

        if not user_input:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Message is required"})
            }

        # Langfuse コールバックの設定
        callbacks = []
        handler = None
        if LANGFUSE_CONF and LANGFUSE_CONF.get("secret_key"):
            try:
                handler = CallbackHandler(
                    public_key=LANGFUSE_CONF["public_key"],
                    secret_key=LANGFUSE_CONF["secret_key"],
                    host=LANGFUSE_CONF["host"],
                    session_id=thread_id,
                    metadata={"user_input": user_input}
                )
                callbacks.append(handler)
                print(f"Langfuse handler initialized for session: {thread_id}")
            except Exception as e:
                global INIT_ERR
                INIT_ERR = str(e)
                print(f"Warning: Failed to initialize CallbackHandler: {e}")
        
        # LangGraph 実行
        graph_config = {
            "configurable": {"thread_id": thread_id},
            "callbacks": callbacks
        }
        input_data = {"messages": [{"role": "user", "content": user_input}]}
        
        output = app.invoke(input_data, graph_config)

        # Langfuse データの送信を強制 (Lambda 終了前に必須)
        if handler:
            try:
                handler.flush()
            except Exception as e:
                print(f"Warning: Failed to flush Langfuse handler: {e}")
        
        # 最後の AI メッセージを取得
        last_msg = output["messages"][-1]
        
        # オブジェクト（AIMessage）と辞書（dict）の両方に対応
        if hasattr(last_msg, "content"):
            response_text = last_msg.content
        elif isinstance(last_msg, dict):
            response_text = last_msg.get("content", "")
        else:
            response_text = str(last_msg)

        # 診断用のサフィックス追加
        handler_type = str(type(handler))
        # 型名に 'langfuse' が含まれ、かつ 'mock' が含まれなければ Real と判定
        is_real = handler is not None and "langfuse" in handler_type.lower() and "mock" not in handler_type.lower()
        conn_type = "Real" if is_real else "Mock"
        
        conf_status = {k: "Present" if v else "Empty" for k, v in (LANGFUSE_CONF or {}).items()}
        suffix = f"\n\n[Final Diagnosis: {conn_type} | Handler: {handler_type} | Conf: {conf_status} | Imp_Err: {IMPORT_ERR} | Init_Err: {INIT_ERR}]"
        response_text += suffix
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "response": response_text,
                "session_id": thread_id
            }, ensure_ascii=False)
        }

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Internal Error: {e}\n{error_detail}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "detail": "Check CloudWatch logs for trace"})
        }
