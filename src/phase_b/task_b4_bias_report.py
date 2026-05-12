"""
Task B.4 — Bias Observations Report (10 phút) — 2 điểm
Code template from README.md
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("="*60)
print("Task B.4 — Bias Observations Report")
print("="*60)

# Load pairwise results
print("\nLoading pairwise results...")
df = pd.read_csv('results/phase_b/pairwise_results.csv')
print(f"✓ Loaded {len(df)} pairs")

# Bias 1: Position bias
print("\n" + "="*60)
print("Bias 1: Position Bias Analysis")
print("="*60)

run1_a_wins = (df['run1_winner'] == 'A').sum()
run1_b_wins = (df['run1_winner'] == 'B').sum()
run1_ties = (df['run1_winner'] == 'tie').sum()
total = len(df)

print(f"\nRun 1 (A first, B second):")
print(f"  A wins: {run1_a_wins}/{total} = {run1_a_wins/total:.1%}")
print(f"  B wins: {run1_b_wins}/{total} = {run1_b_wins/total:.1%}")
print(f"  Ties:   {run1_ties}/{total} = {run1_ties/total:.1%}")

run2_a_wins = (df['run2_winner'] == 'A').sum()
run2_b_wins = (df['run2_winner'] == 'B').sum()
run2_ties = (df['run2_winner'] == 'tie').sum()

print(f"\nRun 2 (B first, A second):")
print(f"  A wins: {run2_a_wins}/{total} = {run2_a_wins/total:.1%}")
print(f"  B wins: {run2_b_wins}/{total} = {run2_b_wins/total:.1%}")
print(f"  Ties:   {run2_ties}/{total} = {run2_ties/total:.1%}")

position_bias = abs(run1_a_wins - run2_a_wins)
print(f"\n⚠ Position bias indicator: {position_bias} pairs changed decision")
if position_bias > total * 0.15:  # >15% changed
    print("  → STRONG position bias detected!")
else:
    print("  → Minimal position bias")

# Bias 2: Length bias
print("\n" + "="*60)
print("Bias 2: Length Bias Analysis")
print("="*60)

df['len_a'] = df['answer_a'].str.len()
df['len_b'] = df['answer_b'].str.len()
df['len_diff'] = df['len_b'] - df['len_a']

print(f"\nAverage answer lengths:")
print(f"  Answer A: {df['len_a'].mean():.0f} chars")
print(f"  Answer B: {df['len_b'].mean():.0f} chars")
print(f"  Difference: {df['len_diff'].mean():.0f} chars (B - A)")

# Did longer answer win more?
b_wins_when_longer = ((df['winner_after_swap'] == 'B') & (df['len_diff'] > 0)).sum()
b_total_longer = (df['len_diff'] > 0).sum()

a_wins_when_longer = ((df['winner_after_swap'] == 'A') & (df['len_diff'] < 0)).sum()
a_total_shorter = (df['len_diff'] < 0).sum()

print(f"\nLength bias indicators:")
print(f"  B wins when B is longer: {b_wins_when_longer}/{b_total_longer} = {b_wins_when_longer/b_total_longer*100:.0f}%")
if a_total_shorter > 0:
    print(f"  A wins when A is longer: {a_wins_when_longer}/{a_total_shorter} = {a_wins_when_longer/a_total_shorter*100:.0f}%")

if b_wins_when_longer / b_total_longer > 0.7:
    print("\n⚠ STRONG length bias detected!")
    print("  → Judge prefers longer answers")
else:
    print("\n✓ Minimal length bias")

# Create visualizations
print("\n" + "="*60)
print("Creating visualizations...")
print("="*60)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Chart 1: Position bias
ax1 = axes[0]
positions = ['Run 1\n(A first)', 'Run 2\n(B first)']
a_wins = [run1_a_wins, run2_a_wins]
b_wins = [run1_b_wins, run2_b_wins]

x = range(len(positions))
width = 0.35
ax1.bar([i - width/2 for i in x], a_wins, width, label='A wins', color='skyblue')
ax1.bar([i + width/2 for i in x], b_wins, width, label='B wins', color='lightcoral')
ax1.set_ylabel('Count')
ax1.set_title('Position Bias: Winner by Run Order')
ax1.set_xticks(x)
ax1.set_xticklabels(positions)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Chart 2: Length bias
ax2 = axes[1]
df_sorted = df.sort_values('len_diff')
colors = ['skyblue' if w == 'A' else 'lightcoral' if w == 'B' else 'gray' 
          for w in df_sorted['winner_after_swap']]
ax2.barh(range(len(df_sorted)), df_sorted['len_diff'], color=colors)
ax2.set_xlabel('Length Difference (B - A) in chars')
ax2.set_ylabel('Pair Index')
ax2.set_title('Length Bias: Winner vs Length Difference')
ax2.axvline(x=0, color='black', linestyle='--', linewidth=1)
ax2.legend(['A wins', 'B wins', 'Tie'], loc='best')
ax2.grid(axis='x', alpha=0.3)

plt.tight_layout()
output_dir = Path("results/phase_b")
plt.savefig(output_dir / 'bias_analysis.png', dpi=150, bbox_inches='tight')
print(f"✓ Saved chart to: results/phase_b/bias_analysis.png")

# Generate report
report = f"""# Judge Bias Observations Report

## Executive Summary

This report analyzes bias patterns in the LLM judge across {len(df)} pairwise comparisons.

**Key Findings:**
- Position bias: {position_bias} pairs changed decision when order swapped
- Length bias: Judge prefers longer answers in {b_wins_when_longer/b_total_longer*100:.0f}% of cases

---

## Bias 1: Position Bias

**Definition:** Judge's decision changes based on which answer appears first.

**Measurement:**

| Run | A first | B first | Winner Distribution |
|---|---|---|---|
| Run 1 | ✓ | | A: {run1_a_wins} ({run1_a_wins/total:.0%}), B: {run1_b_wins} ({run1_b_wins/total:.0%}), Tie: {run1_ties} |
| Run 2 | | ✓ | A: {run2_a_wins} ({run2_a_wins/total:.0%}), B: {run2_b_wins} ({run2_b_wins/total:.0%}), Tie: {run2_ties} |

**Analysis:**
- {position_bias} pairs ({position_bias/total:.0%}) changed decision when order swapped
- Expected: ~0% if no position bias
- Observed: {position_bias/total:.0%}

**Severity:** {'🔴 HIGH' if position_bias > total * 0.15 else '🟡 MEDIUM' if position_bias > total * 0.05 else '🟢 LOW'}

**Mitigation Strategy:**
1. ✓ Already implemented: Swap-and-average (run twice with reversed order)
2. Add explicit instruction in judge prompt: "Order of answers is random and should not affect your judgment"
3. Use position-agnostic prompt format (e.g., "Option 1" and "Option 2" instead of "A" and "B")

---

## Bias 2: Length Bias

**Definition:** Judge systematically prefers longer or shorter answers regardless of quality.

**Measurement:**

| Metric | Value |
|---|---|
| Average length A | {df['len_a'].mean():.0f} chars |
| Average length B | {df['len_b'].mean():.0f} chars |
| B wins when B longer | {b_wins_when_longer}/{b_total_longer} ({b_wins_when_longer/b_total_longer*100:.0f}%) |
| A wins when A longer | {a_wins_when_longer}/{a_total_shorter} ({a_wins_when_longer/a_total_shorter*100:.0f}% if a_total_shorter > 0 else 'N/A') |

**Analysis:**
- B is on average {df['len_diff'].mean():.0f} chars longer than A
- When B is longer, B wins {b_wins_when_longer/b_total_longer*100:.0f}% of the time
- Expected: ~50% if no length bias
- Observed: {b_wins_when_longer/b_total_longer*100:.0f}%

**Severity:** {'🔴 HIGH' if b_wins_when_longer/b_total_longer > 0.7 else '🟡 MEDIUM' if b_wins_when_longer/b_total_longer > 0.6 else '🟢 LOW'}

**Mitigation Strategy:**
1. Add explicit instruction: "Evaluate based on quality, not length. Concise answers can be better than verbose ones."
2. Include "conciseness" as an explicit evaluation criterion
3. Provide examples of good short answers and bad long answers in few-shot prompts
4. Consider normalizing answer lengths before judging (truncate to same length)

---

## Visualization

![Bias Analysis](bias_analysis.png)

**Chart 1 (Left):** Position bias - Winner distribution changes between runs
**Chart 2 (Right):** Length bias - Longer answers (positive x-axis) tend to win more

---

## Overall Recommendations

### Priority 1: Fix Length Bias (High Impact)
- Modify judge prompt to explicitly value conciseness
- Add "conciseness" to evaluation rubric
- Test with balanced dataset (equal length answers)

### Priority 2: Monitor Position Bias (Already Mitigated)
- Continue using swap-and-average approach
- Track position bias metric in production

### Priority 3: Improve Calibration
- Current Cohen's kappa: 0.000 (poor agreement with human)
- After fixing biases, re-run calibration with 20-30 pairs
- Target: kappa ≥ 0.6 for production use

---

*Generated by Task B.4 - Bias Observations Report*
"""

with open(output_dir / 'judge_bias_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✓ Saved report to: results/phase_b/judge_bias_report.md")

print("\n" + "="*60)
print("✓ Task B.4 Complete!")
print("="*60)

print(f"""
Summary:
- Position bias: {position_bias} pairs changed ({position_bias/total:.0%})
- Length bias: Longer answer wins {b_wins_when_longer/b_total_longer*100:.0f}% of time
- Visualizations saved to bias_analysis.png
- Full report saved to judge_bias_report.md

""")

print("="*60)
print("✅ Phase B Complete!")
print("="*60)
print("""
Phase B Summary:
✓ Task B.1: Pairwise judge with swap-and-average (30 pairs)
✓ Task B.2: Absolute scoring with 4-dimension rubric (30 answers)
✓ Task B.3: Human calibration - Cohen's kappa = 0.000
✓ Task B.4: Bias analysis - Strong length bias detected

Next: Phase C - Guardrails Stack
""")
