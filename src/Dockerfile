# 1. AWS Lambda 用の Python 3.11 公式ベースイメージを使用
FROM public.ecr.aws/lambda/python:3.11

# 2. ビルドツールのインストール
# イメージの OS バージョンに合わせ、yum を使用して gcc 等をインストールします。
RUN yum install -y gcc gcc-c++ python3-devel && \
    yum clean all

# 3. 依存ライブラリのインストール
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# 4. ソースコードのコピー
COPY app_crew.py crew_marketing.py ${LAMBDA_TASK_ROOT}/

# 5. Lambda ハンドラーの指定
CMD [ "app_crew.lambda_handler" ]
