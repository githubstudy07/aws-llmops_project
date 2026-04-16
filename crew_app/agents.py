# File: crew_app/agents.py
"""エージェント定義"""

from __future__ import annotations

import os
from crewai import Agent

from crew_app.tools import DuckDuckGoSearchTool


# デフォルト LLM を環境変数で切替可能にする
DEFAULT_LLM = os.environ.get(
    "CREWAI_LLM_MODEL",
    "bedrock/amazon.nova-micro-v1:0",
)


def make_researcher(*, llm: str | None = None) -> Agent:
    """Researcher エージェントを生成する。

    Args:
        llm: 使用する LLM モデル名。None の場合は DEFAULT_LLM を使用。

    Returns:
        Web 検索ツール付きの Researcher Agent
    """
    search_tool = DuckDuckGoSearchTool(
        max_results=5,
        request_timeout=20,
    )

    resolved_llm = llm or DEFAULT_LLM

    return Agent(
        role="Senior Research Analyst",
        goal=(
            "Search the web for the most recent and accurate information "
            "on a given topic and compile a comprehensive research report."
        ),
        backstory=(
            "You are an expert researcher with deep experience in "
            "finding, verifying, and synthesizing information from "
            "multiple web sources. You always cite your sources."
        ),
        tools=[search_tool],
        llm=resolved_llm,
        verbose=True,
        allow_delegation=False,
        # Nova Micro 向け: 最大反復回数を制限して暴走を防止
        max_iter=10,
    )


def make_copywriter(*, llm: str | None = None) -> Agent:
    """Copywriter エージェントを生成する。"""
    resolved_llm = llm or DEFAULT_LLM
    return Agent(
        role="Pro Copywriter",
        goal="Based on the researcher's findings, write high-quality content that engages the reader.",
        backstory=(
            "You are a copywriter familiar with both SEO and reader engagement. "
            "Convert the given information into clear and attractive text."
        ),
        llm=resolved_llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )
