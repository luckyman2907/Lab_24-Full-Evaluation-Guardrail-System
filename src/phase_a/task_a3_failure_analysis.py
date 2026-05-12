"""
Task A.3 — Failure Cluster Analysis (15 phút) — 8 điểm
Identify bottom 10 questions and analyze failure patterns
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*60)
print("Task A.3 — Failure Cluster Analysis")
print("="*60)

# Load RAGAS results
print("\nLoading RAGAS results...")
results = pd.read_csv("results/phase_a/ragas_results.csv")
print(f"✓ Loaded {len(results)} evaluated questions")

# Calculate average score across 4 metrics
results['avg_score'] = results[['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall']].mean(axis=1)

# Get bottom 10 questions
bottom_10 = results.nsmallest(10, 'avg_score')

print(f"\n✓ Identified bottom 10 questions (avg score: {bottom_10['avg_score'].mean():.3f})")

# Analyze patterns and create clusters
# Cluster 1: Low faithfulness (hallucination)
cluster_1 = bottom_10[bottom_10['faithfulness'] < 0.6]

# Cluster 2: Low context precision (irrelevant retrieval)
cluster_2 = bottom_10[bottom_10['context_precision'] < 0.5]

# Cluster 3: Low context recall (missing information)
cluster_3 = bottom_10[bottom_10['context_recall'] < 0.6]

# Generate failure analysis report
report = f"""# Failure Cluster Analysis

## Overview
- **Total questions evaluated**: {len(results)}
- **Bottom 10 average score**: {bottom_10['avg_score'].mean():.3f}
- **Overall average score**: {results['avg_score'].mean():.3f}

## Bottom 10 Questions

| # | Question (truncated) | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---|---|---|---|---|
"""

for idx, (i, row) in enumerate(bottom_10.iterrows(), 1):
    question = row['question'][:50] if 'question' in row else row.get('user_input', '')[:50]
    
    # Assign cluster
    cluster = "C3"  # Default
    if row['faithfulness'] < 0.6:
        cluster = "C1"
    elif row['context_precision'] < 0.5:
        cluster = "C2"
    
    report += f"| {idx} | {question}... | {row['faithfulness']:.2f} | {row['answer_relevancy']:.2f} | {row['context_precision']:.2f} | {row['context_recall']:.2f} | {row['avg_score']:.2f} | {cluster} |\n"

report += f"""

## Clusters Identified

### Cluster C1: Hallucination / Low Faithfulness ({len(cluster_1)} questions)

**Pattern:** Generated answers contain claims not supported by retrieved context.

**Metrics:**
- Average Faithfulness: {cluster_1['faithfulness'].mean():.3f}
- Average Answer Relevancy: {cluster_1['answer_relevancy'].mean():.3f}

**Examples:**
"""

for idx, (i, row) in enumerate(cluster_1.head(2).iterrows(), 1):
    q = row['question'][:80] if 'question' in row else row.get('user_input', '')[:80]
    report += f"- \"{q}...\"\n"

report += f"""

**Root cause:** 
- LLM generating information beyond retrieved context
- Retrieved chunks may be incomplete or ambiguous
- Prompt not emphasizing "only use provided context"

**Proposed fix:**
1. Add explicit instruction in system prompt: "Only answer based on provided context. If information is not in context, say 'I don't have enough information'"
2. Implement citation mechanism - require LLM to cite which context chunk each claim comes from
3. Add post-processing filter to check if answer claims are grounded in context

---

### Cluster C2: Irrelevant Retrieval / Low Context Precision ({len(cluster_2)} questions)

**Pattern:** Retrieved documents are not relevant to the question.

**Metrics:**
- Average Context Precision: {cluster_2['context_precision'].mean():.3f}
- Average Context Recall: {cluster_2['context_recall'].mean():.3f}

**Examples:**
"""

for idx, (i, row) in enumerate(cluster_2.head(2).iterrows(), 1):
    q = row['question'][:80] if 'question' in row else row.get('user_input', '')[:80]
    report += f"- \"{q}...\"\n"

report += f"""

**Root cause:**
- Embedding model not capturing semantic meaning well
- Query too short or ambiguous
- Document chunks too large, containing mixed topics

**Proposed fix:**
1. Implement query expansion - rephrase user query into multiple variations before retrieval
2. Add re-ranker (Cohere Rerank or cross-encoder) after initial retrieval to filter irrelevant chunks
3. Reduce chunk size from 1000 → 500 tokens for more precise retrieval
4. Try hybrid search: BM25 (keyword) + vector search combined

---

### Cluster C3: Missing Information / Low Context Recall ({len(cluster_3)} questions)

**Pattern:** Relevant information exists in corpus but not retrieved.

**Metrics:**
- Average Context Recall: {cluster_3['context_recall'].mean():.3f}
- Average Context Precision: {cluster_3['context_precision'].mean():.3f}

**Examples:**
"""

for idx, (i, row) in enumerate(cluster_3.head(2).iterrows(), 1):
    q = row['question'][:80] if 'question' in row else row.get('user_input', '')[:80]
    report += f"- \"{q}...\"\n"

report += f"""

**Root cause:**
- `top_k` too small (currently 3-5 chunks)
- Multi-hop questions requiring information from multiple documents
- Embedding model bias toward certain document types

**Proposed fix:**
1. Increase `top_k` from 3 → 8 for initial retrieval
2. Implement multi-query retrieval - decompose complex questions into sub-questions
3. Add metadata filtering (e.g., document type, date) to narrow search space
4. Consider using parent-child chunking - retrieve small chunks but provide larger parent context to LLM

---

## Summary Statistics

| Cluster | Count | Avg Faithfulness | Avg Answer Relevancy | Avg Context Precision | Avg Context Recall |
|---|---|---|---|---|---|
| C1 (Hallucination) | {len(cluster_1)} | {cluster_1['faithfulness'].mean():.3f} | {cluster_1['answer_relevancy'].mean():.3f} | {cluster_1['context_precision'].mean():.3f} | {cluster_1['context_recall'].mean():.3f} |
| C2 (Irrelevant Retrieval) | {len(cluster_2)} | {cluster_2['faithfulness'].mean():.3f} | {cluster_2['answer_relevancy'].mean():.3f} | {cluster_2['context_precision'].mean():.3f} | {cluster_2['context_recall'].mean():.3f} |
| C3 (Missing Info) | {len(cluster_3)} | {cluster_3['faithfulness'].mean():.3f} | {cluster_3['answer_relevancy'].mean():.3f} | {cluster_3['context_precision'].mean():.3f} | {cluster_3['context_recall'].mean():.3f} |

## Recommended Priority

1. **High Priority**: Fix Cluster C2 (Irrelevant Retrieval) - Add re-ranker
2. **Medium Priority**: Fix Cluster C1 (Hallucination) - Improve prompt with citation requirement
3. **Low Priority**: Fix Cluster C3 (Missing Info) - Increase top_k and try multi-query

---

*Generated by Task A.3 - Failure Cluster Analysis*
"""

# Save report
output_path = Path("results/phase_a/failure_analysis.md")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✓ Saved failure analysis to: {output_path}")

# Print summary
print("\n" + "="*60)
print("Cluster Summary")
print("="*60)
print(f"C1 (Hallucination):       {len(cluster_1)} questions")
print(f"C2 (Irrelevant Retrieval): {len(cluster_2)} questions")
print(f"C3 (Missing Info):        {len(cluster_3)} questions")
print("="*60)

print("\n✓ Task A.3 Complete!")
print("\nNext: Task A.4 - CI/CD Integration Plan")
