# File: crew_app/app_crew.py
"""
Lambda ハンドラー

Lambda 環境判定:
  - 環境変数 LAMBDA_TASK_ROOT が存在する場合 → Lambda 本番環境
  - 存在しない場合 → ローカル / GitHub Actions テスト環境

pysqlite3 ハックは Lambda 本番環境でのみ適用する。
"""

import os
import sys

# ------------------------------------------------------------------
# [CRITICAL] pysqlite3 ハック: Lambda 本番環境でのみ適用
# ------------------------------------------------------------------
_IS_LAMBDA_RUNTIME = "LAMBDA_TASK_ROOT" in os.environ

if _IS_LAMBDA_RUNTIME:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# ------------------------------------------------------------------
# /tmp へのパス強制リダイレクト
# ------------------------------------------------------------------
_TMP_DIRS = [
    "/tmp/chroma_db",
    "/tmp/crewai_storage",
    "/tmp/huggingface",
    "/tmp/sentence_transformers",
]
for _d in _TMP_DIRS:
    os.makedirs(_d, exist_ok=True)

os.environ.setdefault("CHROMA_DB_PATH", "/tmp/chroma_db")
os.environ.setdefault("CREWAI_STORAGE_DIR", "/tmp/crewai_storage")
os.environ.setdefault("HF_HOME", "/tmp/huggingface")
os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", "/tmp/sentence_transformers")
os.environ.setdefault("HOME", "/tmp")

# ------------------------------------------------------------------
# 通常 import
# ------------------------------------------------------------------
import json
import logging
import boto3
from openinference.instrumentation.crewai import CrewAIInstrumentor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Langfuse 用の計装 (OTel)
CrewAIInstrumentor().instrument()

def _init_langfuse() -> None:
    """
    SSM Parameter Store から Langfuse キーを取得して環境変数に設定する。
    """
    if os.environ.get("LANGFUSE_PUBLIC_KEY"):
        return

    if not _IS_LAMBDA_RUNTIME:
        return

    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
    param_prefix = os.environ.get("SSM_PARAM_PREFIX", "/handson/langfuse")

    try:
        response = ssm.get_parameters(
            Names=[
                f"{param_prefix}/public_key",
                f"{param_prefix}/secret_key",
                f"{param_prefix}/host",
            ],
            WithDecryption=True,
        )
        params = {p["Name"]: p["Value"] for p in response["Parameters"]}
        os.environ["LANGFUSE_PUBLIC_KEY"] = params.get(f"{param_prefix}/public_key", "")
        os.environ["LANGFUSE_SECRET_KEY"] = params.get(f"{param_prefix}/secret_key", "")
        os.environ["LANGFUSE_HOST"] = params.get(f"{param_prefix}/host", "https://cloud.langfuse.com")
        logger.info("Langfuse keys loaded from SSM.")
    except Exception as e:
        logger.warning(f"Failed to load Langfuse keys from SSM: {e}")

_init_langfuse()

# 後続のモジュール import
from crew_app.crew import build_crew


def handler(event: dict, context: object) -> dict:
    """
    API Gateway -> Lambda ハンドラー
    """
    logger.info(f"Event received: {json.dumps(event, ensure_ascii=False)}")

    try:
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)

        # 最新ガイドに合わせ 'topic' を使用
        topic: str = body.get("topic", "")
        if not topic:
            return _response(400, {"error": "topic is required."})

        crew = build_crew(topic=topic)
        result = crew.kickoff(inputs={"topic": topic})

        return _response(200, {"result": str(result)})

    except Exception as e:
        logger.exception("Unhandled error in handler")
        # テストのアサーションに合わせ、エラー内容を直接返す
        return _response(500, {"error": str(e)})


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False),
    }
