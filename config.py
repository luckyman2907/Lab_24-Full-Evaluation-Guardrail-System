"""Configuration for Lab 24 - Evaluation & Guardrails System"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Paths
DOCS_DIR = "./docs"
DATA_DIR = "./data"
RESULTS_DIR = "./results"
LOGS_DIR = "./logs"

# RAGAS Configuration
RAGAS_MODEL = "gpt-4o-mini"
TEST_SET_SIZE = 50
DISTRIBUTION = {
    "simple": 0.5,
    "reasoning": 0.25,
    "multi_context": 0.25
}

# Benchmark Targets
BENCHMARK_TARGETS = {
    "faithfulness": {"target": 0.85, "min_ok": 0.75},
    "answer_relevancy": {"target": 0.80, "min_ok": 0.70},
    "context_precision": {"target": 0.70, "min_ok": 0.60},
    "context_recall": {"target": 0.75, "min_ok": 0.65}
}

# Judge Configuration
JUDGE_MODEL = "gpt-4o-mini"
PAIRWISE_SAMPLES = 30
HUMAN_CALIBRATION_SAMPLES = 10

# Guardrails Configuration
ALLOWED_TOPICS = [
    "artificial intelligence",
    "machine learning",
    "data science",
    "programming",
    "software engineering"
]

# Latency Targets (milliseconds)
LATENCY_TARGETS = {
    "L1_P95": 50,  # Input guardrails
    "L1_TARGET": 30,
    "L3_P95": 100,  # Output guardrails
    "L3_TARGET": 50,
    "TOTAL_P95": 2500  # Total with guardrails
}

# SLOs
SLOS = {
    "faithfulness": {"target": 0.85, "alert_threshold": 0.80, "severity": "P2"},
    "answer_relevancy": {"target": 0.80, "alert_threshold": 0.75, "severity": "P2"},
    "context_precision": {"target": 0.70, "alert_threshold": 0.65, "severity": "P3"},
    "context_recall": {"target": 0.75, "alert_threshold": 0.70, "severity": "P3"},
    "p95_latency": {"target": 2.5, "alert_threshold": 3.0, "severity": "P1"},
    "guardrail_detection_rate": {"target": 0.90, "alert_threshold": 0.85, "severity": "P2"},
    "false_positive_rate": {"target": 0.05, "alert_threshold": 0.10, "severity": "P2"}
}
