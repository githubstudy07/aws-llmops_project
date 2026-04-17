# crew_app/agents.py
"""
エージェント定義
- create_researcher_agent: Web検索担当リサーチャー
- create_writer_agent: コピーライター
- create_archivist_agent: DynamoDB 読み書き担当アーキビスト
"""

import os
from crewai import Agent, LLM
from crew_app.tools import DynamoDBWriteTool, DynamoDBReadTool

# DuckDuckGoSearchTool はオプション（インポート失敗時は None）
try:
    from crew_app.tools import DuckDuckGoSearchTool
    _search_tool = DuckDuckGoSearchTool() if DuckDuckGoSearchTool else None
except Exception:
    _search_tool = None


def _get_llm() -> LLM:
    """
    Bedrock Nova Micro を使用する LLM インスタンスを返す。
    モデル ID は環境変数から取得。
    """
    model_id = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
    return LLM(
        model=f"bedrock/{model_id}",
        temperature=0.3,
    )


def create_researcher_agent() -> Agent:
    """リサーチャーエージェントを生成して返す。"""
    tools = [_search_tool] if _search_tool else []
    return Agent(
        role="Senior Research Analyst",
        goal="与えられたトピックについて正確で最新の情報をWeb検索で収集する",
        backstory=(
            "あなたは経験豊富なリサーチアナリストです。"
            "DuckDuckGo を使い、信頼性の高い情報を効率的に収集できます。"
        ),
        tools=tools,
        llm=_get_llm(),
        verbose=False, # Lambda 環境では False
        allow_delegation=False,
        max_iter=3,
    )


def create_writer_agent() -> Agent:
    """コピーライターエージェントを生成して返す。"""
    return Agent(
        role="Creative Copywriter",
        goal="リサーチ結果をもとに、魅力的な広告コピーを作成する",
        backstory=(
            "あなたはデジタル広告に精通したコピーライターです。"
            "データに基づいた説得力のあるコピーを作成できます。"
        ),
        tools=[],
        llm=_get_llm(),
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )


def create_archivist_agent() -> Agent:
    """
    アーキビスト（記録係）エージェントを生成して返す。
    DynamoDB への読み書きを担当し、エージェント間の長期記憶を管理する。
    """
    return Agent(
        role="Knowledge Archivist",
        goal="調査結果や成果物を DynamoDB に保存・取得し、チームの長期記憶を管理する",
        backstory=(
            "あなたはチームの記録係です。"
            "重要な調査結果や成果物を確実にアーカイブし、"
            "後続タスクで必要な情報を即座に取り出すことができます。"
        ),
        tools=[DynamoDBWriteTool(), DynamoDBReadTool()],
        llm=_get_llm(),
        verbose=False,
        allow_delegation=False,
        max_iter=3,
    )
