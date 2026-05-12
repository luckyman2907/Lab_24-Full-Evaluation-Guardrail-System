"""
Task A.2 — Run RAGAS 4 Metrics (20 phút) — 10 điểm

RAG pipeline: src/rag/pipeline.py (HybridSearch BM25+Dense + CrossEncoder rerank + GPT-4o-mini)
"""

import asyncio
import sys
import os

# Thêm project root vào sys.path để import được 'src.*'
# File này nằm ở src/phase_a/ → project root là 2 cấp lên
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

import os
import json
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# ─────────────────────────────────────────────
# 1. Load RAG pipeline từ Day 18
# ─────────────────────────────────────────────
print("Loading RAG pipeline...")
from src.rag.pipeline import rag_pipeline, RAG_AVAILABLE

if not RAG_AVAILABLE:
    print("⚠ WARNING: RAG pipeline không khởi động được!")
    print("  Kiểm tra lại: docs/ folder có file không? Qdrant có chạy không?")
    sys.exit(1)

print("✓ RAG pipeline ready\n")

# ─────────────────────────────────────────────
# 2. Load test set
# ─────────────────────────────────────────────
print("Loading test set...")
testset = pd.read_csv("results/phase_a/testset_v1.csv")
print(f"✓ Loaded {len(testset)} questions")

# ─────────────────────────────────────────────
# 3. Chạy RAG thật trên từng question
# ─────────────────────────────────────────────
print("\nRunning RAG pipeline on test set...")
print("(HybridSearch BM25+Dense → CrossEncoder rerank → GPT-4o-mini)")

results_data = []
errors = 0

for idx, row in testset.iterrows():
    question     = row['user_input'] if 'user_input' in row else row.get('question', '')
    ground_truth = row.get('reference', row.get('ground_truth', ''))

    try:
        answer, contexts = rag_pipeline(question)

        # RAGAS cần contexts là list[str]
        if isinstance(contexts, list):
            contexts_str = [str(c) for c in contexts]
        else:
            contexts_str = [str(contexts)]

        results_data.append({
            'user_input':         question,
            'response':           answer,
            'retrieved_contexts': contexts_str,
            'reference':          ground_truth,
        })

    except Exception as e:
        print(f"  ⚠ Error on question {idx}: {e}")
        errors += 1
        # Vẫn append để giữ đủ số lượng, RAGAS sẽ skip NaN
        results_data.append({
            'user_input':         question,
            'response':           "",
            'retrieved_contexts': [""],
            'reference':          ground_truth,
        })

    if (idx + 1) % 10 == 0:
        print(f"  Processed {idx + 1}/{len(testset)} questions  (errors so far: {errors})")

print(f"\n✓ Completed: {len(results_data)} questions, {errors} errors")

# ─────────────────────────────────────────────
# 4. Setup RAGAS metrics
# ─────────────────────────────────────────────
print("\nSetting up RAGAS metrics...")

llm = LangchainLLMWrapper(
    ChatOpenAI(model="gpt-4o-mini", timeout=120, max_retries=3)
)
embeddings = LangchainEmbeddingsWrapper(
    OpenAIEmbeddings(model="text-embedding-3-small")
)

metrics = [
    Faithfulness(llm=llm),
    AnswerRelevancy(llm=llm, embeddings=embeddings),
    ContextPrecision(llm=llm),
    ContextRecall(llm=llm),
]

# ─────────────────────────────────────────────
# 5. Evaluate với RAGAS
# ─────────────────────────────────────────────
print("\nEvaluating with RAGAS 4 metrics...")
print("This will take 5-10 minutes...")

dataset = Dataset.from_list(results_data)
scores  = evaluate(dataset, metrics=metrics)

# ─────────────────────────────────────────────
# 6. Save results
# ─────────────────────────────────────────────
print("\nSaving results...")
os.makedirs("results/phase_a", exist_ok=True)

scores_df = scores.to_pandas()
scores_df.to_csv("results/phase_a/ragas_results.csv", index=False)
print("✓ Saved: results/phase_a/ragas_results.csv")

def safe_mean(col: str) -> float:
    return float(scores_df[col].dropna().mean()) if col in scores_df.columns else 0.0

summary = {
    'faithfulness':      safe_mean('faithfulness'),
    'answer_relevancy':  safe_mean('answer_relevancy'),
    'context_precision': safe_mean('context_precision'),
    'context_recall':    safe_mean('context_recall'),
}

with open('results/phase_a/ragas_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("✓ Saved: results/phase_a/ragas_summary.json")

# ─────────────────────────────────────────────
# 7. In kết quả & so sánh target
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("RAGAS Evaluation Summary")
print("=" * 60)
for metric, score in summary.items():
    print(f"  {metric:25s}: {score:.3f}")
print("=" * 60)

targets = {
    'faithfulness':      (0.85, 0.75),
    'answer_relevancy':  (0.80, 0.70),
    'context_precision': (0.70, 0.60),
    'context_recall':    (0.75, 0.65),
}

print("\nTarget Comparison:")
for metric, (target, min_ok) in targets.items():
    score = summary[metric]
    if score >= target:
        status = "✓ Excellent"
    elif score >= min_ok:
        status = "✓ OK"
    else:
        status = "⚠ Below minimum"
    print(f"  {metric:25s}: {score:.3f}  (target: {target:.2f}, min: {min_ok:.2f})  {status}")

print(f"\n  RAG errors: {errors}/{len(testset)} questions failed")
print("\n" + "=" * 60)
print("✓ Task A.2 Complete!")
print("=" * 60)
print("\nNext: Task A.3 - Failure Cluster Analysis")
