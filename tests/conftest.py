# File: tests/conftest.py
import os
import pytest
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# LAMBDA_TASK_ROOT を削除してテスト環境を保証
os.environ.pop("LAMBDA_TASK_ROOT", None)

# テスト用のダミー環境変数
os.environ.setdefault("AWS_DEFAULT_REGION", "ap-northeast-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "test_pub_key")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "test_sec_key")
os.environ.setdefault("LANGFUSE_HOST", "http://localhost:3000")
os.environ.setdefault("CREWAI_STORAGE_DIR", "/tmp/crewai_storage_test")
os.environ.setdefault("CHROMA_DB_PATH", "/tmp/chroma_db_test")
