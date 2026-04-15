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
        role="シニア・リサーチャー",
        goal="指定されたトピックについて徹底的に調査し、正確な情報を収集する",
        backstory=(
            "あなたは 10 年以上の経験を持つシニア・リサーチャーです。"
            "複雑なトピックを分析し、重要なインサイトを抽出することに長けています。"
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )


def make_copywriter() -> Agent:
    llm = _bedrock_llm()
    return Agent(
        role="プロ・コピーライター",
        goal="リサーチャーの調査結果を元に、読者を引きつける高品質なコンテンツを執筆する",
        backstory=(
            "あなたは SEO と読者エンゲージメントの両面に精通したコピーライターです。"
            "与えられた情報を分かりやすく魅力的な文章に変換します。"
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
