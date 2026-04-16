# File: crew_app/tasks.py
"""タスク定義"""

from __future__ import annotations

from crewai import Agent, Task


def make_research_task(*, agent: Agent, topic: str) -> Task:
    """リサーチタスクを生成する。

    Args:
        agent: 担当エージェント
        topic: 調査テーマ

    Returns:
        Task オブジェクト
    """
    return Task(
        description=(
            f"Conduct thorough research on the following topic: '{topic}'.\n\n"
            "You MUST follow these steps exactly:\n\n"
            "Step 1: Use the 'DuckDuckGo Search Tool' to search for the topic.\n"
            "  - To use the tool, provide a search query as input.\n"
            "Step 2: Read the search results carefully.\n"
            "Step 3: Use the 'DuckDuckGo Search Tool' again with a different "
            "query to find additional perspectives.\n"
            "Step 4: Synthesize all findings into a structured report.\n\n"
            "IMPORTANT: You MUST use the search tool at least 2 times "
            "before writing the final report.\n"
        ),
        expected_output=(
            "A research report in the following exact format:\n\n"
            "## Executive Summary\n"
            "(2-3 sentences summarizing the key findings)\n\n"
            "## Key Findings\n"
            "- Finding 1 (Source: URL)\n"
            "- Finding 2 (Source: URL)\n"
            "- Finding 3 (Source: URL)\n\n"
            "## Detailed Analysis\n"
            "(3-5 paragraphs with detailed analysis)\n\n"
            "## Conclusion\n"
            "(2-3 sentences with recommendations)\n"
        ),
        agent=agent,
    )


def make_writing_task(*, agent: Agent, research_task: Task, topic: str) -> Task:
    """執筆タスクを生成する。"""
    return Task(
        description=(
            f"Based on the researcher's findings, write a high-quality article on the topic: '{topic}'.\n\n"
            "- Engaging title and introduction\n"
            "- Structured body based on research findings\n"
            "- Conclusion with a call to action"
        ),
        expected_output=(
            "Completed article (Japanese, Markdown format):\n"
            "- Title\n"
            "- Introduction (200+ characters)\n"
            "- Body (3+ sections)\n"
            "- Conclusion"
        ),
        agent=agent,
        context=[research_task],
    )
