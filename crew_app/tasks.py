# File: crew_app/tasks.py
"""タスク定義 — Phase 9-1 updated."""

from __future__ import annotations

from crewai import Task


def make_research_task(agent, topic: str) -> Task:
    """Web 検索を活用した調査タスクを生成する。

    Args:
        agent: Researcher エージェント
        topic: 調査テーマ
    """
    return Task(
        description=(
            f"Research the topic: '{topic}'.\n"
            "You MUST use the duckduckgo_search tool at least once to find current information.\n"
            "Collect key facts, recent developments, and relevant data.\n"
            "Organize findings in a structured format."
        ),
        expected_output=(
            "A structured report containing:\n"
            "1) 3-5 key facts (bullet points)\n"
            "2) Recent developments\n"
            "3) Eventual sources/URLs found during search"
        ),
        agent=agent,
    )


def make_writing_task(agent, research_task: Task, topic: str) -> Task:
    """調査結果を元にしたライティングタスクを生成する。

    Args:
        agent: Copywriter エージェント
        research_task: 先行する調査タスク
        topic: 調査テーマ
    """
    return Task(
        description=(
            f"Using the research findings provided for the topic '{topic}', "
            "write a concise summary (200 words maximum). "
            "Focus on accuracy and clarity. Do not fabricate information."
        ),
        expected_output="A well-written summary of approximately 150-200 words.",
        agent=agent,
        context=[research_task],
    )
