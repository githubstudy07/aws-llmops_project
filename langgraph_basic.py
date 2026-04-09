import json
import boto3
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from botocore.config import Config

"""
Phase 3: LangGraph 基礎 - 最初のグラフ構築
LangGraph を使用して、単発の Bedrock 呼び出しを「グラフ」として定義します。

### 基本用語
1. State (状態): グラフ内で引き回されるデータ。今回はメッセージのリスト。
2. Node (ノード): 実際の処理を行う関数。
3. Edge (エッジ): ノード間の接続経路。
"""

# 設定
REGION = "ap-northeast-1"
# 💡 東京リージョンから Nova Micro をオンデマンドで利用するための「クロスリージョン推論プロファイル ARN」
# 💡 アジアパシフィック(APAC)地域のクロスリージョン推論プロファイル ID
MODEL_ID = "apac.amazon.nova-micro-v1:0"

# Bedrock Runtime クライアントの初期化
config = Config(read_timeout=300, retries={'max_attempts': 3})
client = boto3.client("bedrock-runtime", region_name=REGION, config=config)

# 1. State (状態) の定義
class State(TypedDict):
    # add_messages は、新しいメッセージを既存のリストに「追加」する特殊な関数
    messages: Annotated[list, add_messages]

# 2. Node (ノード) の定義: AI を呼び出す関数
def chatbot(state: State):
    """
    Converse API を使用して Bedrock を呼び出します。
    """
    # LangGraph の messages 形式を Converse API 形式に変換
    bedrock_messages = []
    for msg in state["messages"]:
        # LangGraph (LangChain) のメッセージオブジェクトから情報を抽出
        # msg.type は 'human' (ユーザー) や 'ai' (アシスタント) になります
        role = "user" if msg.type == "human" else "assistant"
        bedrock_messages.append({
            "role": role,
            "content": [{"text": msg.content}]
        })

    try:
        # Converse API の呼び出し (より推奨される方法)
        response = client.converse(
            modelId=MODEL_ID,
            messages=bedrock_messages,
            system=[{"text": "あなたは簡潔に回答する、親切な AI アシスタントです。"}],
            inferenceConfig={
                "maxTokens": 300,
                "temperature": 0.7
            }
        )
        
        # 応答からテキストを抽出
        output_text = response["output"]["message"]["content"][0]["text"]
        
        # 新しいメッセージを返す (これが自動的に State に合流される)
        return {"messages": [{"role": "assistant", "content": output_text}]}
    
    except Exception as e:
        return {"messages": [{"role": "assistant", "content": f"エラーが発生しました: {str(e)}"}]}

# 3. グラフの構築
# - StateGraph を初期化
workflow = StateGraph(State)

# - ノードを追加
workflow.add_node("chatbot", chatbot)

# - エッジ (流れ) を定義
workflow.add_edge(START, "chatbot") # 開始点から chatbot ノードへ
workflow.add_edge("chatbot", END)    # chatbot ノードから終了点へ

# - コンパイル (実行可能な形式に変換)
app = workflow.compile()

# --- テスト実行 ---
if __name__ == "__main__":
    print("--- LangGraph テスト開始 ---")
    
    # 初回の入力
    initial_input = {"messages": [{"role": "user", "content": "LangGraph を使うメリットを1つ教えて。"}]}
    
    # グラフの実行 (invoke)
    output = app.invoke(initial_input)
    
    # 結果の表示
    for msg in output["messages"]:
        # human / ai のタイプによってアイコンを切り替え
        role_icon = "👤" if msg.type == "human" else "🤖"
        print(f"{role_icon} [{msg.type}]: {msg.content}")
