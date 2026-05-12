"""
Task B.1 — Pairwise Judge Pipeline (20 phút) — 10 điểm
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

JUDGE_PROMPT = PromptTemplate.from_template("""
You are an impartial evaluator. Compare two answers to the same question.

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Rate based on:
- Factual accuracy
- Relevance to question
- Conciseness

Output JSON only:
{{"winner": "A" or "B" or "tie", "reason": "..."}}
""")

def parse_judge_output(text):
    """Robust JSON parsing với fallback."""
    try:
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {"winner": "tie", "reason": "Parse error"}

def pairwise_judge_with_swap(question, ans1, ans2, judge_llm):
    """Swap-and-average for position bias mitigation."""
    results = []

    # Run 1: ans1 first, ans2 second
    prompt = JUDGE_PROMPT.format(
        question=question, answer_a=ans1, answer_b=ans2
    )
    out = judge_llm.invoke(prompt)
    r1 = parse_judge_output(out.content)
    results.append(r1)

    # Run 2: swap order
    prompt = JUDGE_PROMPT.format(
        question=question, answer_a=ans2, answer_b=ans1
    )
    out = judge_llm.invoke(prompt)
    r2 = parse_judge_output(out.content)

    # IMPORTANT: flip winner because order was swapped
    if r2['winner'] == 'A':
        r2['winner'] = 'B'
    elif r2['winner'] == 'B':
        r2['winner'] = 'A'
    results.append(r2)

    # Aggregate: both agree → that. Disagree → tie.
    if results[0]['winner'] == results[1]['winner']:
        return results[0]['winner'], results[0], results[1]
    return 'tie', results[0], results[1]

print("="*60)
print("Task B.1 — Pairwise Judge Pipeline")
print("="*60)

# Setup judge LLM
print("\nSetting up judge LLM...")
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
print("✓ Judge LLM ready")

# Load test set
print("\nLoading test set...")
testset = pd.read_csv("results/phase_a/testset_v1.csv")
print(f"✓ Loaded {len(testset)} questions")

# For demonstration, we'll compare two versions of answers:
# Version A: Short answer
# Version B: Detailed answer
print("\nGenerating two answer versions for comparison...")
print("Note: In production, these would be from different RAG configurations")

# Take first 30 questions
questions_to_judge = testset.head(30)

results = []
for idx, row in questions_to_judge.iterrows():
    question = row['user_input'] if 'user_input' in row else row.get('question', '')
    
    # Simulate two different RAG versions
    # Version A: Short
    answer_a = f"Short answer: {question[:50]}..."
    # Version B: Detailed
    answer_b = f"Detailed answer with more context: {question[:50]}... This provides additional information and explanation."
    
    # Judge with swap
    winner, run1, run2 = pairwise_judge_with_swap(question, answer_a, answer_b, judge_llm)
    
    results.append({
        'question': question[:100],
        'answer_a': answer_a[:100],
        'answer_b': answer_b[:100],
        'winner_after_swap': winner,
        'run1_winner': run1['winner'],
        'run2_winner': run2['winner'],
        'run1_reason': run1.get('reason', ''),
        'run2_reason': run2.get('reason', '')
    })
    
    if (idx + 1) % 10 == 0:
        print(f"  Judged {idx + 1}/{len(questions_to_judge)} pairs")

print(f"\n✓ Completed pairwise judging for {len(results)} pairs")

# Save results
output_dir = Path("results/phase_b")
output_dir.mkdir(parents=True, exist_ok=True)

results_df = pd.DataFrame(results)
results_df.to_csv(output_dir / "pairwise_results.csv", index=False)
print(f"✓ Saved results to: results/phase_b/pairwise_results.csv")

# Print summary
print("\n" + "="*60)
print("Pairwise Judge Summary")
print("="*60)
print(f"Total pairs judged: {len(results)}")
print(f"Winner distribution:")
print(f"  A wins: {(results_df['winner_after_swap'] == 'A').sum()}")
print(f"  B wins: {(results_df['winner_after_swap'] == 'B').sum()}")
print(f"  Ties:   {(results_df['winner_after_swap'] == 'tie').sum()}")

# Check consistency (run1 vs run2)
consistent = (results_df['run1_winner'] == results_df['run2_winner']).sum()
print(f"\nConsistency (both runs agree): {consistent}/{len(results)} ({consistent/len(results)*100:.1f}%)")

print("\n" + "="*60)
print("✓ Task B.1 Complete!")
print("="*60)
print("\nNext: Task B.2 - Absolute Scoring with Rubric")
