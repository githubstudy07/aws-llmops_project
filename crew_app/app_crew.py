# crew_app/app_crew.py
"""
Lambda エントリーポイント
- API Gateway からのリクエストを受け取り、Crew を実行して結果を返す
"""

import json
import os
import uuid
import logging
from crewai import Crew, Process

from crew_app.tasks import (
    create_research_task,
    create_writing_task,
    create_archive_task,
    create_read_task,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: dict, context) -> dict:
    """
    Lambda ハンドラー関数。
    API Gateway からの POST リクエストを処理する。
    """
    try:
        # リクエストボディのパース
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
            
        topic = body.get("topic", "AIエージェント最新動向")
        mode = body.get("mode", "full")
        content_id = body.get("content_id", f"research-{uuid.uuid4().hex[:8]}")

        logger.info(f"Execution started. mode={mode}, topic={topic}, content_id={content_id}")

        if mode == "read":
            # 読み取りモード
            read_task, archivist = create_read_task(content_id)
            crew = Crew(
                agents=[archivist],
                tasks=[read_task],
                process=Process.sequential,
                verbose=False,
            )
        else:
            # フルモード: リサーチ → コピー作成 → アーカイブ
            research_task, researcher = create_research_task(topic)
            write_task, writer = create_writing_task([research_task])
            archive_task, archivist = create_archive_task(content_id, [write_task])

            crew = Crew(
                agents=[researcher, writer, archivist],
                tasks=[research_task, write_task, archive_task],
                process=Process.sequential,
                verbose=False,
            )

        result = crew.kickoff()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "status": "success",
                    "mode": mode,
                    "topic": topic,
                    "content_id": content_id,
                    "result": str(result),
                },
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"status": "error", "message": str(e)},
                ensure_ascii=False,
            ),
        }

# SAM 対応のため handler エイリアスを作成
def handler(event, context):
    return lambda_handler(event, context)
