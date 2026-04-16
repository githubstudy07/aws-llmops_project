# File: crew_app/tasks.py
"""タスク定義 — Phase 9-1 & 9-2."""

from __future__ import annotations

from crewai import Task


def make_research_task(agent, topic: str) -> Task:
    """Web 検索を活用した調査タスクを生成する。"""
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
    """調査結果を元にしたライティングタスクを生成する。"""
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


def make_archive_task(agent, content_id: str, context_task: Task) -> Task:
    """成果物を DynamoDB に保存するタスクを生成する。"""
    return Task(
        description=(
            f"Save the output of the previous task to DynamoDB archive.\n\n"
            f"【Procedure】\n"
            f"1. Use the 'dynamodb_write' tool.\n"
            f"2. Set 'content_id' to '{content_id}'.\n"
            f"3. Set 'content' to the FULL text from the previous task.\n"
            f"4. Confirm that the data was successfully saved.\n\n"
            "You MUST use the dynamodb_write tool."
        ),
        expected_output=(
            f"Final confirmation message stating the data was saved with content_id='{content_id}'."
        ),
        agent=agent,
        context=[context_task],
    )


def make_retrieve_task(agent, content_id: str) -> Task:
    """DynamoDB から過去の成果物を取得するタスクを生成する。"""
    return Task(
        description=(
            f"Retrieve a previously saved report from DynamoDB.\n\n"
            f"【Procedure】\n"
            f"1. Use the 'dynamodb_read' tool.\n"
            f"2. Set 'content_id' to '{content_id}'.\n"
            f"3. Summarize the retrieved content.\n\n"
            "You MUST use the dynamodb_read tool."
        ),
        expected_output=(
            f"A summary of the record found with content_id='{content_id}', "
            "or a message reporting that no record was found."
        ),
        agent=agent,
    )
