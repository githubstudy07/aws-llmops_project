FROM public.ecr.aws/lambda/python:3.12

# 依存関係のコピーとインストール
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピー
COPY app_crew.py crew_marketing.py ${LAMBDA_TASK_ROOT}/

# ハンドラー指定
CMD [ "app_crew.lambda_handler" ]
