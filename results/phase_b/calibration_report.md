# Human Calibration Report

## Cohen's Kappa Analysis

**Kappa Score**: 0.000

**Interpretation**: Slight agreement — không tin được

**Status**: ❌ Poor

## Agreement Statistics

- Total pairs evaluated: 10
- Agreements: 3/10 (30%)
- Disagreements: 7/10 (70%)

## Confusion Matrix

| Human \ Judge | A | B | tie |
|---|---|---|---|
| A | 0 | 4 | 0 |
| B | 0 | 3 | 0 |
| tie | 0 | 3 | 0 |


## Recommendations

⚠ Kappa < 0.6 indicates moderate to low agreement.

**Possible causes:**
1. Judge prompt may have biases (position, length, style)
2. Human labeling may be inconsistent
3. Task definition may be ambiguous

**Next steps:**
1. Review judge prompt for clarity
2. Analyze bias patterns in Task B.4
3. Consider labeling more pairs (20-30) for better calibration
