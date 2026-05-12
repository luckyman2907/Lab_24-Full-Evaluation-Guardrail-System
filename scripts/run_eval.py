#!/usr/bin/env python3
"""
Evaluation script for CI/CD pipeline
Usage: python scripts/run_eval.py --threshold faithfulness=0.85
"""

import argparse
import json
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run RAGAS evaluation with threshold gate')
    parser.add_argument('--threshold', type=str, required=True, 
                       help='Threshold in format: metric=value (e.g., faithfulness=0.85)')
    args = parser.parse_args()
    
    # Parse threshold
    metric_name, threshold_str = args.threshold.split('=')
    threshold = float(threshold_str)
    
    print(f"Checking {metric_name} >= {threshold}")
    
    # Load RAGAS summary
    summary_path = Path("results/phase_a/ragas_summary.json")
    if not summary_path.exists():
        print(f"❌ Error: {summary_path} not found")
        print("Run evaluation first: python src/phase_a/task_a2_run_ragas.py")
        sys.exit(1)
    
    with open(summary_path) as f:
        summary = json.load(f)
    
    # Check threshold
    if metric_name not in summary:
        print(f"❌ Error: Metric '{metric_name}' not found in summary")
        print(f"Available metrics: {list(summary.keys())}")
        sys.exit(1)
    
    score = summary[metric_name]
    print(f"\n{metric_name}: {score:.3f}")
    
    if score >= threshold:
        print(f"✓ PASS: {score:.3f} >= {threshold}")
        sys.exit(0)
    else:
        print(f"❌ FAIL: {score:.3f} < {threshold}")
        print(f"\nEvaluation gate failed. Please improve RAG quality before merging.")
        sys.exit(1)

if __name__ == "__main__":
    main()
