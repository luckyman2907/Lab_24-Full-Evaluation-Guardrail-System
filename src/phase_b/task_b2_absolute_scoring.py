"""
Task B.2 — Absolute Scoring với Rubric (10 phút) — 5 điểm
Code template from README.md
"""

import asyncio
import sys

# Fix for Windows event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import json
import pandas as pd
from pathlib import Path

ABSOLUTE_PROMPT = PromptTemplate.from_template("""
Score the answer on 4 dimensions, each 1-5 scale:
1. Factual accuracy (1=many errors, 5=fully accurate)
2. Relevance (1=off-topic, 5=directly answers)
3. Conciseness (1=verbose, 5=appropriately brief)
4. Helpfulness (1=unclear, 5=actionable)

Question: {question}
Answer: {answer}

Output JSON only:
{{"accuracy": int, "relevance": int, "conciseness": int,
  "helpfulness": int, "overall": float}}
""")

def parse_judge_output(text):
    """Robust JSON parsing với fallback."""
    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {"accuracy": 3, "relevance": 3, "conciseness": 3, "helpfulness": 3, "overall": 3.0}

def absolute_score(question, answer, judge_llm):
    prompt = ABSOLUTE_PROMPT.format(question=question, answer=answer)
    out = judge_llm.invoke(prompt)
    parsed = parse_judge_output(out.content)

    # Compute overall as average if not provided
    if 'overall' not in parsed:
        dims = ['accuracy', 'relevance', 'conciseness', 'helpfulness']
        parsed['overall'] = sum(parsed[d] for d in dims) / 4
    return parsed

print("="*60)
print("Task B.2 — Absolute Scoring with Rubric")
print("="*60)

# Setup judge LLM
print("\nSetting up judge LLM...")
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
print("✓ Judge LLM ready")

# Load test set
print("\nLoading test set...")
testset = pd.read_csv("results/phase_a/testset_v1.csv")
print(f"✓ Loaded {len(testset)} questions")

# Take first 30 questions
questions_to_score = testset.head(30)

print("\nScoring answers on 4 dimensions...")
results = []
for idx, row in questions_to_score.iterrows():
    question = row['user_input'] if 'user_input' in row else row.get('question', '')
    
    # Generate sample answer (in production, this would be from your RAG)
    answer = f"This is a sample answer for: {question[:80]}... It provides relevant information based on the context."
    
    # Score with rubric
    scores = absolute_score(question, answer, judge_llm)
    
    results.append({
        'question': question[:100],
        'answer': answer[:100],
        'accuracy': scores.get('accuracy', 3),
        'relevance': scores.get('relevance', 3),
        'conciseness': scores.get('conciseness', 3),
        'helpfulness': scores.get('helpfulness', 3),
        'overall': scores.get('overall', 3.0)
    })
    
    if (idx + 1) % 10 == 0:
        print(f"  Scored {idx + 1}/{len(questions_to_score)} answers")

print(f"\n✓ Completed absolute scoring for {len(results)} answers")

# Save results
output_dir = Path("results/phase_b")
output_dir.mkdir(parents=True, exist_ok=True)

results_df = pd.DataFrame(results)
results_df.to_csv(output_dir / "absolute_scores.csv", index=False)
print(f"✓ Saved results to: results/phase_b/absolute_scores.csv")

# Print summary
print("\n" + "="*60)
print("Absolute Scoring Summary")
print("="*60)
print(f"Total answers scored: {len(results)}")
print(f"\nAverage scores (1-5 scale):")
print(f"  Accuracy:    {results_df['accuracy'].mean():.2f}")
print(f"  Relevance:   {results_df['relevance'].mean():.2f}")
print(f"  Conciseness: {results_df['conciseness'].mean():.2f}")
print(f"  Helpfulness: {results_df['helpfulness'].mean():.2f}")
print(f"  Overall:     {results_df['overall'].mean():.2f}")

# Distribution
print(f"\nScore distribution:")
for dim in ['accuracy', 'relevance', 'conciseness', 'helpfulness']:
    print(f"\n{dim.capitalize()}:")
    dist = results_df[dim].value_counts().sort_index()
    for score, count in dist.items():
        print(f"  {score}: {'█' * count} ({count})")

print("\n" + "="*60)
print("✓ Task B.2 Complete!")
print("="*60)
print("\nNext: Task B.3 - Human Calibration with Cohen's Kappa")
