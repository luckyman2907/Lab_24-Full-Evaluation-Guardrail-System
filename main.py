"""
Main runner for Lab 24 - Full Evaluation & Guardrail System

This script orchestrates all 4 phases:
- Phase A: RAGAS Evaluation
- Phase B: LLM-as-Judge & Calibration
- Phase C: Guardrails Stack
- Phase D: Blueprint Document

Usage:
    python main.py --all                    # Run all phases
    python main.py --phase A                # Run specific phase
    python main.py --phase A --phase B      # Run multiple phases
"""

import argparse
import asyncio
from pathlib import Path

import config
from src.phase_a_ragas import RAGASEvaluator, demo_rag_pipeline
from src.phase_b_judge import LLMJudge, generate_demo_data
from src.phase_c_guardrails import (
    InputGuard, TopicGuard, OutputGuardAPI,
    GuardrailsTester, benchmark_full_stack
)
from src.phase_d_blueprint import generate_blueprint


def setup_directories():
    """Create necessary directories"""
    Path(config.RESULTS_DIR).mkdir(exist_ok=True)
    Path(config.DATA_DIR).mkdir(exist_ok=True)
    Path(config.LOGS_DIR).mkdir(exist_ok=True)
    Path(config.DOCS_DIR).mkdir(exist_ok=True)
    print("✓ Directories created")


def run_phase_a():
    """Run Phase A: RAGAS Evaluation"""
    print("\n" + "=" * 70)
    print(" " * 20 + "PHASE A: RAGAS EVALUATION")
    print("=" * 70)
    
    evaluator = RAGASEvaluator()
    
    # Task A.1: Generate test set
    print("\n[Task A.1] Generating synthetic test set...")
    testset_df = evaluator.task_a1_generate_testset()
    
    # Task A.2: Run RAGAS metrics
    print("\n[Task A.2] Running RAGAS evaluation...")
    print("⚠ Note: This requires a working RAG pipeline.")
    print("Using demo pipeline for now. Replace with your Day 18 RAG pipeline.")
    
    try:
        summary = evaluator.task_a2_run_ragas_metrics(testset_df, demo_rag_pipeline)
        
        # Task A.3: Failure analysis
        print("\n[Task A.3] Performing failure cluster analysis...")
        import pandas as pd
        results_df = pd.read_csv(f"{config.RESULTS_DIR}/ragas_results.csv")
        bottom_10 = evaluator.task_a3_failure_analysis(results_df)
    except Exception as e:
        print(f"⚠ Skipping A.2 and A.3 due to: {e}")
        print("Please implement your RAG pipeline and run again.")
    
    # Task A.4: CI/CD integration
    print("\n[Task A.4] Creating CI/CD integration files...")
    evaluator.task_a4_cicd_integration()
    
    print("\n✓ Phase A Complete!")


def run_phase_b():
    """Run Phase B: LLM-as-Judge & Calibration"""
    print("\n" + "=" * 70)
    print(" " * 15 + "PHASE B: LLM-AS-JUDGE & CALIBRATION")
    print("=" * 70)
    
    judge = LLMJudge()
    
    # Generate demo data
    questions, answers_a, answers_b = generate_demo_data(config.PAIRWISE_SAMPLES)
    
    # Task B.1: Pairwise evaluation
    print("\n[Task B.1] Running pairwise judge pipeline...")
    pairwise_df = judge.run_pairwise_evaluation(questions, answers_a, answers_b)
    
    # Task B.2: Absolute scoring
    print("\n[Task B.2] Running absolute scoring...")
    absolute_df = judge.run_absolute_scoring(questions, answers_a)
    
    # Task B.3: Human calibration
    print("\n[Task B.3] Setting up human calibration...")
    kappa = judge.task_b3_human_calibration(pairwise_df, config.HUMAN_CALIBRATION_SAMPLES)
    
    if kappa is None:
        print("\n⚠ Please complete human labeling in results/human_labels.csv")
        print("Then run Phase B again to compute Cohen's kappa")
    
    # Task B.4: Bias analysis
    print("\n[Task B.4] Analyzing judge biases...")
    judge.task_b4_bias_analysis(pairwise_df)
    
    print("\n✓ Phase B Complete!")


def run_phase_c():
    """Run Phase C: Guardrails Stack"""
    print("\n" + "=" * 70)
    print(" " * 20 + "PHASE C: GUARDRAILS STACK")
    print("=" * 70)
    
    # Initialize components
    input_guard = InputGuard()
    topic_guard = TopicGuard(config.ALLOWED_TOPICS, method="embedding")
    output_guard = OutputGuardAPI()
    tester = GuardrailsTester()
    
    # Task C.1: PII redaction
    print("\n[Task C.1] Testing PII redaction...")
    tester.task_c1_test_pii_redaction(input_guard)
    
    # Task C.2: Topic validator
    print("\n[Task C.2] Testing topic validator...")
    tester.task_c2_test_topic_validator(topic_guard)
    
    # Task C.3: Adversarial testing
    print("\n[Task C.3] Running adversarial tests...")
    tester.task_c3_adversarial_testing(input_guard, topic_guard)
    
    # Task C.4: Output guardrail
    print("\n[Task C.4] Testing output guardrail (Llama Guard)...")
    if config.GROQ_API_KEY:
        tester.task_c4_test_output_guard(output_guard)
    else:
        print("⚠ GROQ_API_KEY not set. Skipping Llama Guard tests.")
        print("Set GROQ_API_KEY in .env to enable output guardrails.")
    
    # Task C.5: Full stack benchmark
    print("\n[Task C.5] Running full stack latency benchmark...")
    asyncio.run(benchmark_full_stack(100))
    
    print("\n✓ Phase C Complete!")


def run_phase_d():
    """Run Phase D: Blueprint Document"""
    print("\n" + "=" * 70)
    print(" " * 20 + "PHASE D: BLUEPRINT DOCUMENT")
    print("=" * 70)
    
    blueprint_path = generate_blueprint()
    
    print("\n✓ Phase D Complete!")
    print(f"\nBlueprint document created at: {blueprint_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Lab 24 - Full Evaluation & Guardrail System"
    )
    parser.add_argument(
        '--phase',
        action='append',
        choices=['A', 'B', 'C', 'D'],
        help='Phase to run (can specify multiple times)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all phases'
    )
    
    args = parser.parse_args()
    
    # Setup
    print("=" * 70)
    print(" " * 10 + "LAB 24: FULL EVALUATION & GUARDRAIL SYSTEM")
    print("=" * 70)
    print("\nSetting up directories...")
    setup_directories()
    
    # Determine which phases to run
    if args.all:
        phases = ['A', 'B', 'C', 'D']
    elif args.phase:
        phases = args.phase
    else:
        # Default: run all phases
        phases = ['A', 'B', 'C', 'D']
    
    # Run phases
    if 'A' in phases:
        run_phase_a()
    
    if 'B' in phases:
        run_phase_b()
    
    if 'C' in phases:
        run_phase_c()
    
    if 'D' in phases:
        run_phase_d()
    
    # Summary
    print("\n" + "=" * 70)
    print(" " * 25 + "LAB 24 COMPLETE!")
    print("=" * 70)
    print("\nResults saved in:", config.RESULTS_DIR)
    print("\nNext steps:")
    print("1. Review all results in the results/ directory")
    print("2. Complete human labeling in results/human_labels.csv (if Phase B ran)")
    print("3. Review the blueprint document: results/blueprint_document.md")
    print("4. Integrate with your Day 18 RAG pipeline")
    print("5. Deploy to production following the blueprint guide")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
