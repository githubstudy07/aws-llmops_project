# File: crew_app/app_crew.py
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
# 通常 import (pysqlite3 ハック適用後に行う)
# ------------------------------------------------------------------
import json
import logging
import boto3
from openinference.instrumentation.crewai import CrewAIInstrumentor

# ログ設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 観測性 (OTel -> Langfuse) のセットアップ
# ※環境変数がセットされている前提で、ライブラリが自動で計装を行う
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
    # プロジェクトの既存プレフィックスを使用
    param_prefix = "/handson/langfuse"

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
        
        # OTel Exporter 用の環境変数 (Langfuse が OTLP 互換の場合。通常は SDK が処理)
        # 念のため SDK が期待する環境変数を固定
        logger.info("Langfuse keys loaded from SSM.")
    except Exception as e:
        logger.warning(f"Failed to load Langfuse keys from SSM: {e}")

# 初期化実行
_init_langfuse()

# 後続の import
from crew_app.crew import build_crew

def handler(event, context):
    """
    API Gateway -> Lambda ハンドラー
    """
    logger.info(f"Event received: {json.dumps(event, ensure_ascii=False)}")
    
    try:
        # リクエストボディのパース
        body = event.get("body", "{}")
        if isinstance(body, str):
            payload = json.loads(body)
        else:
            payload = body
            
        target_product = payload.get("target_product", "新しい健康飲料")
        
        # Crew の構築と実行
        crew = build_crew()
        result = crew.kickoff(inputs={"target_product": target_product})
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": "CrewAI execution successful",
                "target_product": target_product,
                "result": str(result)
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.exception("Internal Server Error")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": "Internal Server Error",
                "details": str(e)
            }, ensure_ascii=False)
        }
