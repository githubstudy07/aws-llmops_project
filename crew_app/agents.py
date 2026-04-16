# File: crew_app/agents.py
"""
CrewAI エージェント定義
Phase 9-2: アーキビストエージェントを追加
"""

import os
from crewai import Agent, LLM
from crew_app.tools import DynamoDBWriteTool, DynamoDBReadTool


def get_llm() -> LLM:
    """
    Bedrock LLM インスタンスを生成する。
    環境変数 BEDROCK_MODEL_ID からモデルIDを取得。
    """
    model_id = os.environ.get("BEDROCK_MODEL_ID", "us.amazon.nova-micro-v1:0")
    return LLM(
        model=f"bedrock/{model_id}",
        temperature=0.3,
    )


def create_researcher_agent() -> Agent:
    """
    リサーチャーエージェント。
    Phase 9-2 では検索ツールを除外（Lambda環境でのDuckDuckGo 403回避）。
    自身の知識に基づいて回答する。
    """
    return Agent(
        role="Senior Researcher",
        goal="指定されたトピックについて、正確で有用な情報を整理して提供する",
        backstory=(
            "あなたは経験豊富なリサーチャーです。"
            "与えられたトピックについて、自身の知識に基づいて"
            "簡潔かつ正確な調査レポートを作成してください。"
            "外部検索ツールは現在利用できません。"
        ),
        llm=get_llm(),
        tools=[],  # Phase 9-2: 検索ツール除外（DuckDuckGo 403 回避）
        verbose=False,  # Lambda環境ではFalse（エンコーディング問題回避）
        max_iter=5,  # ループ防止（課金制御）
    )


def create_archivist_agent() -> Agent:
    """
    アーキビスト（記録係）エージェント。
    DynamoDB への読み書きツールを使用して成果物を管理する。
    """
    return Agent(
        role="Research Archivist",
        goal="リサーチ結果を DynamoDB に正確に保存し、過去の成果物を検索・取得する",
        backstory=(
            "あなたは成果物管理の専門家です。"
            "リサーチャーから受け取った調査結果を、適切な識別子を付けて"
            "データベースに保存します。"
            "content_id は 'research-YYYYMMDD-連番' 形式で生成してください。"
            "保存が完了したら、使用した content_id を必ず報告してください。"
        ),
        llm=get_llm(),
        tools=[DynamoDBWriteTool(), DynamoDBReadTool()],
        verbose=False,
        max_iter=5,
    )
