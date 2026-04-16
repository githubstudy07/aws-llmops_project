# crew_app/tasks.py
"""
タスク定義
- create_research_task: Web検索・情報収集タスク
- create_writing_task: 広告コピー作成タスク
- create_archive_task: DynamoDB アーカイブタスク
- create_read_task: DynamoDB 読み取りタスク
"""

from crewai import Task
from crew_app.agents import (
    create_researcher_agent,
    create_writer_agent,
    create_archivist_agent,
)


def create_research_task(topic: str) -> tuple[Task, object]:
    """リサーチタスクとエージェントを生成して返す。"""
    researcher = create_researcher_agent()
    task = Task(
        description=(
            f"'{topic}' について、最新の情報をWeb検索で収集してください。\n"
            "収集した情報は箇条書き形式で整理し、出典URLも含めてください。"
        ),
        expected_output=(
            "・調査トピックの概要\n"
            "・主要な調査結果（箇条書き5項目以上）\n"
            "・参考URL一覧"
        ),
        agent=researcher,
    )
    return task, researcher


def create_writing_task(context_tasks: list) -> tuple[Task, object]:
    """コピー作成タスクとエージェントを生成して返す。"""
    writer = create_writer_agent()
    task = Task(
        description=(
            "リサーチ結果をもとに、ターゲット顧客に響く広告コピーを3パターン作成してください。\n"
            "各パターンにキャッチコピー（30文字以内）と本文（100文字以内）を含めること。"
        ),
        expected_output=(
            "【パターン1】\n"
            "キャッチコピー: ...\n"
            "本文: ...\n\n"
            "【パターン2】\n"
            "キャッチコピー: ...\n"
            "本文: ...\n\n"
            "【パターン3】\n"
            "キャッチコピー: ...\n"
            "本文: ..."
        ),
        agent=writer,
        context=context_tasks,
    )
    return task, writer


def create_archive_task(content_id: str, context_tasks: list) -> tuple[Task, object]:
    """
    DynamoDB アーカイブタスクとアーキビストエージェントを生成して返す。
    前タスクの結果を content_id をキーに保存する。
    """
    archivist = create_archivist_agent()
    task = Task(
        description=(
            f"前のタスクで得られた成果物（リサーチ結果または広告コピー）を、\n"
            f"content_id='{content_id}' として DynamoDB Write Tool を使って保存してください。\n"
            "保存が成功したことを確認してください。"
        ),
        expected_output=(
            f"DynamoDB への保存成功メッセージ（content_id: {content_id} を含むこと）"
        ),
        agent=archivist,
        context=context_tasks,
    )
    return task, archivist


def create_read_task(content_id: str) -> tuple[Task, object]:
    """
    DynamoDB 読み取りタスクとアーキビストエージェントを生成して返す。
    """
    archivist = create_archivist_agent()
    task = Task(
        description=(
            f"DynamoDB Read Tool を使用して、\n"
            f"content_id='{content_id}' のレコードを取得してください。"
        ),
        expected_output=(
            "取得したレコードの内容（content_id と content を含むこと）"
        ),
        agent=archivist,
    )
    return task, archivist
