# File: src/Dockerfile
FROM public.ecr.aws/lambda/python:3.12

# 依存関係インストール（キャッシュ効率のため先にコピー）
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# アプリケーションコード
COPY main.py ${LAMBDA_TASK_ROOT}/

# Lambda ハンドラー指定
CMD ["main.lambda_handler"]
