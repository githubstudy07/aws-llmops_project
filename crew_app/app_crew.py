# crew_app/app_crew.py
"""
Lambda エントリーポイント
- API Gateway からのリクエストを受け取り、Crew を実行して結果を返す
"""

import json
import os
import uuid
import logging
import boto3
from crewai import Crew, Process

from crew_app.tasks import (
    create_research_task,
    create_writing_task,
    create_archive_task,
    create_read_task,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_langfuse_handler(content_id: str):
    """SSM からキーを取得し、Langfuse (LiteLLM) 連携を有効化する"""
    try:
        # SSM からパラメータ取得
        ssm = boto3.client("ssm", region_name="ap-northeast-1")
        prefix = os.environ.get("SSM_PARAM_PREFIX", "/handson/langfuse")
        params = ssm.get_parameters_by_path(Path=prefix, WithDecryption=True)
        param_dict = {p["Name"].split("/")[-1]: p["Value"] for p in params["Parameters"]}
        
        pk = param_dict.get("public_key")
        sk = param_dict.get("secret_key")
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
        
        if pk and sk:
            import litellm
            os.environ["LANGFUSE_PUBLIC_KEY"] = pk
            os.environ["LANGFUSE_SECRET_KEY"] = sk
            os.environ["LANGFUSE_HOST"] = host
            
            # success_callback に "langfuse_otel" を追加することで自動トレースを有効化
            # Langfuse SDK v4+ に推奨される方式
            if "langfuse_otel" not in litellm.success_callback:
                litellm.success_callback.append("langfuse_otel")
            
            logger.info("Langfuse (LiteLLM OTEL callback) enabled successfully.")
            return True
    except Exception as e:
        logger.warning(f"Langfuse enablement failed: {str(e)}")
    return False

def lambda_handler(event: dict, context) -> dict:
    """
    Lambda ハンドラー関数。
    API Gateway からの POST リクエストを処理する。
    """
    try:
        # リクエストボディのパース
        body = event.get("body")
        if body is None:
            body = {}
        elif isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse body: {body}")
                body = {}
            
        topic = body.get("topic", "AIエージェント最新動向")
        mode = body.get("mode", "full")
        content_id = body.get("content_id", f"research-{uuid.uuid4().hex[:8]}")

        logger.info(f"Execution started. mode={mode}, topic={topic}, content_id={content_id}")

        # Langfuse 監視の有効化 (OTel)
        langfuse_enabled = get_langfuse_handler(content_id)

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

        # Crew 実行 (callbacks を渡す)
        from langfuse import propagate_attributes
        with propagate_attributes(session_id=content_id):
            # CrewAI v1.x: LiteLLM callback により自動的にトレースが収集される
            result = crew.kickoff()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Trace-Id": content_id # セッションIDをトレース識別子として返却
            },
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
