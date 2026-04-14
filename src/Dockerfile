# 1. AWS Lambda 用の Python 3.11 公式ベースイメージを使用
FROM public.ecr.aws/lambda/python:3.11

# 2. 依存ライブラリのインストール
# ※ コンテナ内でビルドすることで、Pydantic v2 等のバイナリ互換性問題を解消します。
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# 3. ソースコードのコピー
COPY app_crew.py crew_marketing.py ${LAMBDA_TASK_ROOT}/

# 4. Lambda ハンドラーの指定
CMD [ "app_crew.lambda_handler" ]
