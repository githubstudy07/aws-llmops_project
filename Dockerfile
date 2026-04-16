# File: Dockerfile
FROM public.ecr.aws/lambda/python:3.12

# システム依存ライブラリのインストール
# (pysqlite3-binary の動作を安定させるため、sqlite-devel を含める)
RUN dnf install -y gcc gcc-c++ make sqlite-devel && \
    dnf clean all

WORKDIR ${LAMBDA_TASK_ROOT}

# Python 依存関係インストール (本番用)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをパッケージとしてコピー
COPY crew_app/ ./crew_app/

# /tmp 配下の環境変数を設定 (Redirection)
ENV TMPDIR=/tmp
ENV HOME=/tmp
ENV CHROMA_DB_PATH=/tmp/chroma_db
ENV CREWAI_STORAGE_DIR=/tmp/crewai_storage
ENV HF_HOME=/tmp/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/sentence_transformers

# ハンドラー指定 (パッケージ形式)
CMD ["crew_app.app_crew.lambda_handler"]
