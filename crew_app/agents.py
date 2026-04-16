# File: crew_app/agents.py
"""エージェント定義 — Phase 9-1 & 9-2."""

from __future__ import annotations

import os

from crewai import Agent

from crew_app.tools import DuckDuckGoSearchTool, DynamoDBReadTool, DynamoDBWriteTool

# デフォルト LLM を環境変数で切替可能にする
DEFAULT_LLM = os.environ.get(
    "CREWAI_LLM_MODEL",
    "bedrock/us.amazon.nova-micro-v1:0",
)


def make_researcher(*, llm: str | None = None) -> Agent:
    """Researcher エージェントを生成する。"""
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
            "multiple web sources. You always use your search tool (duckduckgo_search) "
            "to verify facts with current web sources."
        ),
        tools=[DuckDuckGoSearchTool()],
        llm=resolved_llm,
        verbose=True,
        # Nova Micro 向け: 最大反復回数を制限して暴走を防止
        max_iter=3,
        max_retry_limit=1,
        allow_delegation=False,
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
        max_iter=3,
    )


def make_archivist(*, llm: str | None = None) -> Agent:
    """アーキビスト（記録係）エージェントを生成する。"""
    resolved_llm = llm or DEFAULT_LLM
    return Agent(
        role="Data Archivist",
        goal=(
            "Accurately save research results and reports into DynamoDB "
            "and retrieve past data as needed."
        ),
        backstory=(
            "You are a specialist in data archiving. You systematically organize "
            "information and store it in persistent storage. You can also "
            "efficiently search and retrieve previously stored data."
        ),
        llm=resolved_llm,
        tools=[DynamoDBWriteTool(), DynamoDBReadTool()],
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
