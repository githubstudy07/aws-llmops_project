import os
from crewai import Agent, Task, Crew, Process
from langchain_aws import ChatBedrock
from openinference.instrumentation.crewai import CrewAIInstrumentor

# ---------------------------------------------------------
# 1. 観測性 (Langfuse) のセットアップ
# ---------------------------------------------------------
# 本番環境では環境変数から読み込まれますが、
# CrewAI の計装を初期化することで、全ステップをトレース可能にします。
CrewAIInstrumentor().instrument()

# ---------------------------------------------------------
# 2. LLM (Bedrock Nova Micro) の設定
# ---------------------------------------------------------
# コスト最小化のため、Nova Micro を使用します。
llm = ChatBedrock(
    model_id="amazon.nova-micro-v1:0",
    model_kwargs={"temperature": 0.3},
)

# ---------------------------------------------------------
# 3. エージェントの設計 (Phase 7-1)
# ---------------------------------------------------------

# リサーチャー：市場の悩みや課題を特定する役割
researcher = Agent(
    role="市場トレンド調査員",
    goal="{target_product} に関する消費者の悩みと、解決のキーワードを3つ特定する",
    backstory=(
        "あなたは広告代理店の優秀なリサーチャーです。"
        "消費者が抱える潜在的な不満やニーズを言葉にすることに長けています。"
    ),
    llm=llm,
    allow_delegation=False, # コスト抑制のため、他Agentへの勝手な委任を禁止
    max_iter=3,             # 【重要】試行回数を最大3回に制限してコスト最小化
    verbose=True            # 思考プロセスを表示（学習用）
)

# コピーライター：リサーチ結果を魅力的な言葉に変換する役割
writer = Agent(
    role="クリエイティブ・コピーライター",
    goal="リサーチ結果を元に、消費者の心に刺さるキャッチコピーを3案作成する",
    backstory=(
        "あなたは数々のヒット作を手がけたコピーライターです。"
        "リサーチ結果にある『生の悩み』を、希望を与える言葉に変える天才です。"
    ),
    llm=llm,
    allow_delegation=False,
    max_iter=3,
    verbose=True
)

# ---------------------------------------------------------
# 4. タスクの設計 (Phase 7-1)
# ---------------------------------------------------------

# タスク1: 市場リサーチ
research_task = Task(
    description=(
        "1. {target_product} を利用しそうなユーザーが、日常で抱えている悩みやストレスを分析してください。\n"
        "2. その悩みに対する解決策を象徴するキーワードを3つ抽出してください。"
    ),
    expected_output="ユーザーの悩み TOP3 と、解決のヒントになるキーワード 3 つのリスト。",
    agent=researcher
)

# タスク2: コピー作成
writing_task = Task(
    description=(
        "リサーチ結果を活用して、{target_product} の魅力を伝えるキャッチコピーを3案作成してください。\n"
        "各案には、なぜその言葉がターゲットに刺さるのかの短い解説を添えてください。"
    ),
    expected_output="3つのキャッチコピー案（各案に解説付き）。",
    agent=writer,
    context=[research_task] # 前のタスクの結果を受け取る設定
)

# ---------------------------------------------------------
# 5. Crew (チーム) の結成と実行
# ---------------------------------------------------------

marketing_crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential, # 順番に進める（最も安価で確実な方法）
    verbose=True
)

# ※ 実際の実行は Lambda や GitHub Actions 上で行います。
# ここでは設計のプレビューとして記述しています。
if __name__ == "__main__":
    # テスト実行用の入力
    inputs = {"target_product": "AI搭載のスマート水筒（水分補給のタイミングを教える）"}
    # result = marketing_crew.kickoff(inputs=inputs)
    # print("\n\n########################")
    # print("## 最終アウトプット")
    # print("########################\n")
    # print(result)
    print("CrewAI Agent script created. Ready for integration.")
