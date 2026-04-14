# 1. AWS Lambda 用の Python 3.12 公式ベースイメージを使用
FROM public.ecr.aws/lambda/python:3.12

# 2. ビルドツールのインストール
# AL2023 (Python 3.12) では yum の代わりに microdnf を使用します。
RUN microdnf install -y gcc gcc-c++ python3-devel && \
    microdnf clean all

# 3. 依存ライブラリのインストール
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# 4. ソースコードのコピー
COPY app_crew.py crew_marketing.py ${LAMBDA_TASK_ROOT}/

# 5. Lambda ハンドラーの指定
CMD [ "app_crew.lambda_handler" ]
