# File: crew_app/tasks.py
"""
CrewAI タスク定義
Phase 9-2: アーカイブタスクを追加
"""

from crewai import Task
from crew_app.agents import create_researcher_agent, create_archivist_agent


def create_research_task(topic: str) -> Task:
    """
    リサーチタスク: 指定トピックについて調査レポートを作成する。
    """
    return Task(
        description=(
            f"以下のトピックについて調査し、要点を日本語で簡潔にまとめてください。\n"
            f"トピック: {topic}\n"
            f"回答は300文字以内で、箇条書きを含めてください。"
        ),
        expected_output="トピックに関する簡潔な調査レポート（日本語・300文字以内・箇条書き含む）",
        agent=create_researcher_agent(),
    )


def create_archive_task(topic: str) -> Task:
    """
    アーカイブタスク: リサーチ結果を DynamoDB に保存する。
    前タスクの出力を受け取り、DynamoDB に書き込む。
    """
    # content_id 用にトピックをサニタイズ
    safe_topic = topic[:20].replace(" ", "-").replace("/", "-").lower()

    return Task(
        description=(
            f"前のタスクで得られたリサーチ結果を DynamoDB に保存してください。\n"
            f"dynamodb_write ツールを使用し、以下のパラメータで保存してください:\n"
            f"- content_id: 'research-{safe_topic}'\n"
            f"- content: 前のタスクのリサーチ結果全文\n"
            f"保存が完了したら、使用した content_id を報告してください。"
        ),
        expected_output="DynamoDB への保存完了メッセージと使用した content_id",
        agent=create_archivist_agent(),
    )
