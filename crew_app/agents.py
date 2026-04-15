# File: crew_app/agents.py
import os
from crewai import Agent, LLM

def _bedrock_llm() -> LLM:
    """
    Amazon Bedrock Nova Micro を CrewAI LLM として返す。
    """
    return LLM(
        model="bedrock/amazon.nova-micro-v1:0",
        region_name=os.environ.get("AWS_REGION", "ap-northeast-1"),
    )

def make_researcher() -> Agent:
    llm = _bedrock_llm()
    return Agent(
        role="市場トレンド調査員",
        goal="{target_product} に関する消費者の悩みと、解決のキーワードを3つ特定する",
        backstory=(
            "あなたは広告代理店の優秀なリサーチャーです。"
            "消費者が抱える潜在的な不満やニーズを言葉にすることに長けています。"
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

def make_copywriter() -> Agent:
    llm = _bedrock_llm()
    return Agent(
        role="クリエイティブ・コピーライター",
        goal="リサーチ結果を元に、消費者の心に刺さるキャッチコピーを3案作成する",
        backstory=(
            "あなたは数々のヒット作を手がけたコピーライターです。"
            "リサーチ結果にある『生の悩み』を、希望を与える言葉に変える天才です。"
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
