import json
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "apac.amazon.nova-micro-v1:0")
LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY")

# Initialize Langfuse Client
client = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY
)

# Initialize LLM
llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    model_kwargs={"temperature": 0.7}
)

# Load Prompts from JSON
def load_prompts(filepath: str) -> Dict:
    """Load variant prompts from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['prompts']

prompts = load_prompts("phase_10_5_7_c_prompts.json")
SYSTEM_PROMPT_A = prompts['variant_a']['system_prompt']
SYSTEM_PROMPT_B = prompts['variant_b']['system_prompt']

def load_dataset(filepath: str) -> List[Dict]:
    """Load test dataset from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['dataset']

def evaluate_response(response: str, expected_keywords: List[str]) -> Dict:
    """Simple evaluation: keyword match and length."""
    response_lower = response.lower()
    keyword_matches = sum(1 for kw in expected_keywords if kw.lower() in response_lower)

    # Scoring: keyword match (0-50) + response length indicator (0-50)
    keyword_score = (keyword_matches / len(expected_keywords)) * 50 if expected_keywords else 0
    length_score = min(50, len(response) / 100)  # Normalized to 100 chars = 50 points
    total_score = keyword_score + length_score

    return {
        "score": round(total_score, 2),
        "keyword_matches": keyword_matches,
        "response_length": len(response),
        "expected_keywords_count": len(expected_keywords)
    }

def run_experiment(dataset: List[Dict], system_prompt: str, variant_name: str, session_id: str) -> List[Dict]:
    """Run all questions with specified system prompt."""
    results = []

    for idx, item in enumerate(dataset):
        question = item['question']
        expected_keywords = item.get('expected_keywords', [])

        try:
            # Invoke LLM
            messages = [HumanMessage(content=f"{system_prompt}\n\nQuestion: {question}")]
            response = llm.invoke(messages)
            answer = response.content

            # Evaluate response
            evaluation = evaluate_response(answer, expected_keywords)

            # Record to Langfuse with trace
            trace_id = f"{session_id}-{variant_name}-{idx}"
            trace = client.trace(
                id=trace_id,
                name=f"Phase10_5_7C_{variant_name}",
                session_id=session_id,
                tags=[variant_name, "ab-test", "prompt-optimization"]
            )

            # Create span for this question
            span = trace.span(
                name=f"question_{item['id']}",
                input={"question": question, "system_prompt": system_prompt[:50] + "..."},
                output={"answer": answer[:100] + "..." if len(answer) > 100 else answer},
                metadata={"variant": variant_name}
            )

            # Record evaluation score
            client.score(
                trace_id=trace.id,
                name="response_quality",
                value=evaluation['score'],
                comment=f"Keyword matches: {evaluation['keyword_matches']}/{evaluation['expected_keywords_count']}, Response length: {evaluation['response_length']} chars"
            )

            result = {
                "question_id": item['id'],
                "question": question,
                "answer": answer,
                "evaluation": evaluation,
                "trace_id": trace_id
            }
            results.append(result)
            logger.info(f"[{variant_name}] Q{idx+1}: Score={evaluation['score']}")

        except Exception as e:
            logger.error(f"Error processing question {item['id']}: {str(e)}")
            results.append({
                "question_id": item['id'],
                "question": question,
                "error": str(e)
            })

    return results

def run_ab_test():
    """Execute A/B test with Baseline and Improved prompts."""
    logger.info("=" * 60)
    logger.info("Phase 10-5-7-C: Prompt A/B Test Started")
    logger.info("=" * 60)

    # Load dataset
    dataset = load_dataset("phase_10_5_7_c_dataset.json")
    logger.info(f"Loaded {len(dataset)} questions")

    # Generate session ID
    session_id = f"phase-10-5-7-c-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Run Variant A (Baseline)
    logger.info("\n--- Running Variant A (Baseline) ---")
    results_a = run_experiment(dataset, SYSTEM_PROMPT_A, "Variant_A_Baseline", session_id)

    # Run Variant B (Improved)
    logger.info("\n--- Running Variant B (Improved) ---")
    results_b = run_experiment(dataset, SYSTEM_PROMPT_B, "Variant_B_Improved", session_id)

    # Calculate aggregate metrics
    scores_a = [r['evaluation']['score'] for r in results_a if 'evaluation' in r]
    scores_b = [r['evaluation']['score'] for r in results_b if 'evaluation' in r]

    avg_score_a = sum(scores_a) / len(scores_a) if scores_a else 0
    avg_score_b = sum(scores_b) / len(scores_b) if scores_b else 0
    improvement = ((avg_score_b - avg_score_a) / avg_score_a * 100) if avg_score_a > 0 else 0

    # Prepare comparison report
    report = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "variant_a_baseline": {
                "avg_score": round(avg_score_a, 2),
                "total_questions": len(scores_a),
                "scores": scores_a
            },
            "variant_b_improved": {
                "avg_score": round(avg_score_b, 2),
                "total_questions": len(scores_b),
                "scores": scores_b
            },
            "improvement_percentage": round(improvement, 2)
        },
        "detailed_results": {
            "variant_a": results_a,
            "variant_b": results_b
        }
    }

    # Save report
    report_filename = f"phase_10_5_7_c_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    logger.info("\n" + "=" * 60)
    logger.info("A/B Test Comparison Summary")
    logger.info("=" * 60)
    logger.info(f"Variant A (Baseline) Average Score: {avg_score_a:.2f}")
    logger.info(f"Variant B (Improved) Average Score: {avg_score_b:.2f}")
    logger.info(f"Improvement: {improvement:.2f}%")
    logger.info(f"Report saved to: {report_filename}")
    logger.info("=" * 60)

    # Flush Langfuse client to ensure all traces are sent
    client.flush()
    logger.info("Langfuse traces flushed.")

    return report

if __name__ == "__main__":
    run_ab_test()
