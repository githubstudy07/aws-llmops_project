# File: local_test.py
"""Phase 9-2: Local E2E Test with DynamoDB Archivist."""

import os
import sys
import json
from datetime import datetime, timezone

# ---- SQLite hack ----
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

# ---- 環境設定 ----
os.environ.setdefault("ARCHIVE_TABLE", "handson-research-archives")
os.environ.setdefault("CREWAI_STORAGE_DIR", "/tmp/crewai_storage")
os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")

from crew_app.crew import build_crew
from crew_app.tools import DynamoDBReadTool


def main():
    topic = "AWS Bedrock Nova latest updates April 2026"
    test_id = f"test_research_{datetime.now(timezone.utc).strftime('%H%M%S')}"

    print(f"{'=' * 60}")
    print(f"Phase 9-2 Local E2E Test")
    print(f"Topic      : {topic}")
    print(f"Content ID : {test_id}")
    print(f"{'=' * 60}\n")

    # Crew の構築
    crew = build_crew(topic=topic, content_id=test_id)
    
    # 実行
    print("Starting Crew...")
    result = crew.kickoff()
    
    print(f"\n{'=' * 60}")
    print("CREW RESULT:")
    print(f"{'=' * 60}")
    print(result)

    # --- 保存されたデータの検証 ---
    print(f"\n{'=' * 60}")
    print("VERIFICATION: Reading from DynamoDB")
    print(f"{'=' * 60}")
    
    reader = DynamoDBReadTool()
    db_result = reader._run(content_id=test_id)
    print(db_result)


if __name__ == "__main__":
    main()
