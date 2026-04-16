# File: crew_app/app_crew.py
"""
Lambda ハンドラー: CrewAI エントリーポイント
Phase 9-2: リサーチ → アーカイブ の Sequential Crew
"""

import json
import logging
import os

from crewai import Crew, Process
from crew_app.tasks import create_research_task, create_archive_task

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Langfuse 初期化（既存処理を維持） ---
# Langfuse の CallbackHandler 初期化コードがある場合はここに配置
# from langfuse.callback import CallbackHandler as LangfuseCallbackHandler
# langfuse_handler = LangfuseCallbackHandler(...)


def handler(event, context):
    """
    Lambda ハンドラー。
    入力: {"body": "{\"topic\": \"...\"}"}
    出力: {"statusCode": 200, "body": "{\"status\": \"success\", ...}"}
    """
    try:
        # --- リクエスト解析 ---
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        topic = body.get("topic", "AI の最新トレンド")

        logger.info(f"Crew 実行開始: topic='{topic}'")

        # --- タスク生成 ---
        research_task = create_research_task(topic)
        archive_task = create_archive_task(topic)

        # --- Crew 構成 ---
        crew = Crew(
            agents=[research_task.agent, archive_task.agent],
            tasks=[research_task, archive_task],
            process=Process.sequential,  # リサーチ → アーカイブ の順序実行
            verbose=False,  # Lambda環境ではFalse
        )

        # --- 実行 ---
        result = crew.kickoff()

        logger.info(f"Crew 実行完了: result_length={len(str(result))}")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "status": "success",
                    "topic": topic,
                    "result": str(result),
                },
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        logger.error(f"Crew 実行エラー: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "status": "error",
                    "message": str(e),
                },
                ensure_ascii=False,
            ),
        }
