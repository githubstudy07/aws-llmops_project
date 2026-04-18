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
        host = os.environ.get("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        
        if pk and sk:
            import litellm
            from langfuse import Langfuse
            from opentelemetry import trace
            from openinference.instrumentation.crewai import CrewAIInstrumentor
            
            # 環境変数を設定（LiteLLM や OTel 連携が参照するため）
            os.environ["LANGFUSE_PUBLIC_KEY"] = pk
            os.environ["LANGFUSE_SECRET_KEY"] = sk
            os.environ["LANGFUSE_HOST"] = host
            
            # 1. Langfuse v4 クライアントの初期化
            # SDK v4 は内部で自動的に OTel TracerProvider を構成します。
            langfuse_client = Langfuse(public_key=pk, secret_key=sk, host=host)
            
            # 2. instrumentation の初期化 (Lambda 再利用時は一度だけ実行)
            provider = trace.get_tracer_provider()
            # 既に TracerProvider が構成済みか、インスツルメンテーション済みかをチェック
            if not hasattr(provider, "add_span_processor"):
                # NoOpProvider の場合、あるいは未初期化の場合
                # 注意: Langfuse v4 は自動で provider をセットアップするため、
                # ここに到達した時点で provider は sdk.trace.TracerProvider になっているはずです
                logger.info("OTel provider initialized via Langfuse v4.")
            
            # 計装は一回のみ実行
            try:
                # 既に計装されているか判定するフラグ等の代わりに簡易的な重複排除
                # CrewAIInstrumentor().instrument() は内部で冪等である場合が多いが
                # ログ出力を制御
                CrewAIInstrumentor().instrument()
                logger.info("CrewAI instrumentation enabled.")
            except Exception as ie:
                logger.debug(f"Instrumentation skip/failed: {str(ie)}")
            
            # 診断用: 接続テスト
            if langfuse_client.auth_check():
                logger.info(f"Langfuse Auth Check: SUCCESS (Host: {host})")
            else:
                logger.error(f"Langfuse Auth Check: FAILED. Check keys for {host}")
            
            # LiteLLM callback を OTel 経由に統一
            litellm.callbacks = []
            litellm.success_callback = ["langfuse_otel"]
            
            logger.info("Langfuse (langfuse_otel) and OTel pipeline ready.")
            return langfuse_client
    except Exception as e:
        logger.warning(f"Langfuse enablement failed: {str(e)}")
    return None

def lambda_handler(event: dict, context) -> dict:
    """
    Lambda ハンドラー関数。
    API Gateway からの POST リクエストを処理する。
    """
    langfuse_client = None
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
        langfuse_client = get_langfuse_handler(content_id)

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

        # Crew 実行
        # Langfuse v4: OTel エクスポーターの設定と litellm callback により
        # 自動的にトレースが収集される構成。
        from langfuse import propagate_attributes
        with propagate_attributes(session_id=content_id):
            result = crew.kickoff()

        # 結果を返す前に強制 Flush (Lambda の凍結対策)
        if langfuse_client:
            logger.info("Flushing Langfuse traces...")
            langfuse_client.flush()
            
        # LiteLLM のコールバックを明示的にフラッシュ
        try:
            import litellm
            litellm.flush_callbacks()
            logger.info("LiteLLM callbacks flushed.")
        except Exception as e:
            logger.warning(f"LiteLLM flush failed: {str(e)}")
            
        # OTel の バッチプロセッサを強制フラッシュ (最優先是正)
        try:
            from opentelemetry import trace
            provider = trace.get_tracer_provider()
            if hasattr(provider, 'force_flush'):
                logger.info("Force flushing OTel TracerProvider...")
                provider.force_flush(timeout_millis=30000)
        except Exception as e:
            logger.warning(f"OTel force_flush failed: {str(e)}")

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
