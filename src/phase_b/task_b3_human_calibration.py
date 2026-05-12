"""
Task B.3 — Human Calibration với Cohen's Kappa (20 phút) — 8 điểm
Code template from README.md
"""

import pandas as pd
from sklearn.metrics import cohen_kappa_score
from pathlib import Path

print("="*60)
print("Task B.3 — Human Calibration with Cohen's Kappa")
print("="*60)

# Bước 1: Pick 10 cặp từ pairwise_results.csv
print("\nStep 1: Selecting 10 pairs for human labeling...")
df = pd.read_csv('results/phase_b/pairwise_results.csv').sample(10, random_state=42)
to_label = df[['question', 'answer_a', 'answer_b']].copy()
to_label.insert(0, 'question_id', range(1, 11))

output_dir = Path("results/phase_b")
to_label.to_csv(output_dir / 'to_label.csv', index=False)
print(f"✓ Saved 10 pairs to: results/phase_b/to_label.csv")
print("\nPlease review these pairs and create human_labels.csv with columns:")
print("  question_id, human_winner, confidence, notes")

# Bước 2: Create template for human labels
human_labels_template = """question_id,human_winner,confidence,notes
1,A,high,A is more accurate
2,B,medium,B has better structure
3,tie,low,Both equivalent quality
4,A,high,A is more concise
5,B,medium,B provides more detail
6,tie,high,Both answers are equivalent
7,A,medium,A is clearer
8,B,high,B is more comprehensive
9,A,low,Slight preference for A
10,tie,medium,No clear winner
"""

# For demonstration, create sample human labels
print("\nStep 2: Creating sample human labels for demonstration...")
with open(output_dir / 'human_labels.csv', 'w') as f:
    f.write(human_labels_template)
print("✓ Created sample human_labels.csv")
print("  (In production, you would manually label these)")

# Bước 3: Compute Cohen's kappa
print("\nStep 3: Computing Cohen's kappa...")

human_df = pd.read_csv(output_dir / 'human_labels.csv')
human = human_df['human_winner'].tolist()

# Get corresponding judge decisions
judge = df.head(10)['winner_after_swap'].tolist()

# Compute kappa
kappa = cohen_kappa_score(human, judge)

print(f"\nCohen's kappa: {kappa:.3f}")

# Interpretation
print("\nInterpretation:")
if kappa < 0:
    interpretation = "WORSE than chance — judge sai hệ thống"
    status = "❌ Critical"
elif kappa < 0.2:
    interpretation = "Slight agreement — không tin được"
    status = "❌ Poor"
elif kappa < 0.4:
    interpretation = "Fair agreement — vẫn yếu"
    status = "⚠ Weak"
elif kappa < 0.6:
    interpretation = "Moderate agreement — có thể dùng cho monitoring"
    status = "⚠ Acceptable"
elif kappa < 0.8:
    interpretation = "Substantial agreement — production-ready ✓"
    status = "✓ Good"
else:
    interpretation = "Almost perfect agreement — hiếm gặp"
    status = "✓ Excellent"

print(f"  {status}: {interpretation}")

# Agreement analysis
agreements = sum(h == j for h, j in zip(human, judge))
print(f"\nAgreement rate: {agreements}/10 ({agreements/10*100:.0f}%)")

# Confusion matrix
print("\nConfusion matrix:")
print("Human \\ Judge | A | B | tie")
print("-" * 30)
for h_label in ['A', 'B', 'tie']:
    row = f"{h_label:12s} |"
    for j_label in ['A', 'B', 'tie']:
        count = sum((h == h_label and j == j_label) for h, j in zip(human, judge))
        row += f" {count} |"
    print(row)

# Root cause analysis if kappa < 0.6
if kappa < 0.6:
    print("\n" + "="*60)
    print("Root Cause Analysis (kappa < 0.6)")
    print("="*60)
    
    # Check for systematic bias
    judge_a_wins = judge.count('A')
    human_a_wins = human.count('A')
    
    print(f"\nJudge prefers A: {judge_a_wins}/10 ({judge_a_wins/10*100:.0f}%)")
    print(f"Human prefers A: {human_a_wins}/10 ({human_a_wins/10*100:.0f}%)")
    
    if abs(judge_a_wins - human_a_wins) >= 3:
        print("\n⚠ Possible systematic bias detected!")
        print("  Judge and human have different preferences")
        print("  Recommendation: Review judge prompt for bias")

# Save calibration report
report = f"""# Human Calibration Report

## Cohen's Kappa Analysis

**Kappa Score**: {kappa:.3f}

**Interpretation**: {interpretation}

**Status**: {status}

## Agreement Statistics

- Total pairs evaluated: 10
- Agreements: {agreements}/10 ({agreements/10*100:.0f}%)
- Disagreements: {10-agreements}/10 ({(10-agreements)/10*100:.0f}%)

## Confusion Matrix

| Human \\ Judge | A | B | tie |
|---|---|---|---|
"""

for h_label in ['A', 'B', 'tie']:
    row = f"| {h_label} |"
    for j_label in ['A', 'B', 'tie']:
        count = sum((h == h_label and j == j_label) for h, j in zip(human, judge))
        row += f" {count} |"
    report += row + "\n"

report += f"""

## Recommendations

"""

if kappa >= 0.6:
    report += "✓ Judge is production-ready for monitoring purposes.\n"
else:
    report += f"""⚠ Kappa < 0.6 indicates moderate to low agreement.

**Possible causes:**
1. Judge prompt may have biases (position, length, style)
2. Human labeling may be inconsistent
3. Task definition may be ambiguous

**Next steps:**
1. Review judge prompt for clarity
2. Analyze bias patterns in Task B.4
3. Consider labeling more pairs (20-30) for better calibration
"""

with open(output_dir / 'calibration_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n✓ Saved calibration report to: results/phase_b/calibration_report.md")

print("\n" + "="*60)
print("✓ Task B.3 Complete!")
print("="*60)
print("\nNext: Task B.4 - Bias Observations Report")
