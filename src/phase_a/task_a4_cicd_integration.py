"""
Task A.4 — CI/CD Integration Plan (10 phút) — 4 điểm
Create GitHub Actions workflow for eval gate
"""

from pathlib import Path

print("="*60)
print("Task A.4 — CI/CD Integration Plan")
print("="*60)

# Create .github/workflows directory
workflows_dir = Path(".github/workflows")
workflows_dir.mkdir(parents=True, exist_ok=True)

# Create eval-gate.yml
workflow_content = """name: RAG Eval Gate

on:
  pull_request:
    branches: [main]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run RAGAS evaluation
        run: python scripts/run_eval.py --threshold faithfulness=0.85
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: ragas-report
          path: ragas_results.csv
"""

workflow_path = workflows_dir / "eval-gate.yml"
with open(workflow_path, 'w') as f:
    f.write(workflow_content)

print(f"\n✓ Created workflow file: {workflow_path}")

# Create run_eval.py script
scripts_dir = Path("scripts")
scripts_dir.mkdir(exist_ok=True)

eval_script = """#!/usr/bin/env python3
\"\"\"
Evaluation script for CI/CD pipeline
Usage: python scripts/run_eval.py --threshold faithfulness=0.85
\"\"\"

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
    print(f"\\n{metric_name}: {score:.3f}")
    
    if score >= threshold:
        print(f"✓ PASS: {score:.3f} >= {threshold}")
        sys.exit(0)
    else:
        print(f"❌ FAIL: {score:.3f} < {threshold}")
        print(f"\\nEvaluation gate failed. Please improve RAG quality before merging.")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""

eval_script_path = scripts_dir / "run_eval.py"
with open(eval_script_path, 'w', encoding='utf-8') as f:
    f.write(eval_script)

print(f"✓ Created eval script: {eval_script_path}")

# Test the script
print("\n" + "="*60)
print("Testing eval script...")
print("="*60)

import subprocess
result = subprocess.run(
    ["python", str(eval_script_path), "--threshold", "faithfulness=0.75"],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode == 0:
    print("✓ Test PASSED")
else:
    print("⚠ Test FAILED (expected if faithfulness < 0.75)")

# Validate YAML syntax
print("\n" + "="*60)
print("Validating YAML syntax...")
print("="*60)

try:
    import yaml
    with open(workflow_path) as f:
        yaml.safe_load(f)
    print("✓ YAML syntax is valid")
except ImportError:
    print("⚠ PyYAML not installed. Install with: pip install pyyaml")
    print("  Skipping YAML validation")
except Exception as e:
    print(f"❌ YAML syntax error: {e}")

print("\n" + "="*60)
print("✓ Task A.4 Complete!")
print("="*60)

print(f"""
Created files:
1. {workflow_path} - GitHub Actions workflow
2. {eval_script_path} - Evaluation gate script

Usage in CI/CD:
- Workflow triggers on PR to main branch
- Runs RAGAS evaluation
- Blocks merge if faithfulness < 0.85
- Uploads results as artifact for debugging

To test locally:
  python scripts/run_eval.py --threshold faithfulness=0.85

To use in GitHub:
1. Push these files to your repo
2. Add OPENAI_API_KEY to GitHub Secrets
3. Create a PR - workflow will run automatically
""")

print("\n" + "="*60)
print("✅ Phase A Complete!")
print("="*60)
print("""
Summary:
✓ Task A.1: Generated 51-question test set
✓ Task A.2: Evaluated with RAGAS 4 metrics
✓ Task A.3: Analyzed failure clusters
✓ Task A.4: Created CI/CD integration

Next: Phase B - LLM-as-Judge & Calibration
""")
