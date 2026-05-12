"""
Task C.1 — Input Guardrail: PII Redaction
Implement Presidio + custom VN regex for PII detection and redaction.
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import re
import time
import pandas as pd
from pathlib import Path

# Vietnamese PII patterns
VN_PII = {
    "cccd":      r"\b\d{12}\b",           # Citizen ID
    "phone_vn":  r"(\+84|0)\d{9,10}",
    "tax_code":  r"\b\d{10}(-\d{3})?\b",
    "email":     r"\b[\w.-]+@[\w.-]+\.\w+\b",
}

class InputGuard:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

    def scrub_vn(self, t):
        """Layer 1: VN-specific regex."""
        for name, pattern in VN_PII.items():
            t = re.sub(pattern, f"[{name.upper()}]", t)
        return t

    def scrub_ner(self, t):
        """Layer 2: Presidio NER (multilingual)."""
        results = self.analyzer.analyze(text=t, language="en")
        return self.anonymizer.anonymize(
            text=t, analyzer_results=results
        ).text

    def sanitize(self, t):
        """Full pipeline with latency tracking."""
        start = time.perf_counter()
        out = self.scrub_ner(self.scrub_vn(t))
        latency_ms = (time.perf_counter() - start) * 1000
        return out, latency_ms


# Test set with 10 inputs containing PII
test_inputs = [
    # English NER
    "Hi, I'm John Smith from Microsoft. Email: john@ms.com",
    "Call me at +1-555-1234 or visit 123 Main Street, NYC",
    # VN regex
    "Số CCCD của tôi là 012345678901",
    "Liên hệ qua 0987654321 hoặc tax 0123456789-001",
    # Mixed
    "Customer Nguyễn Văn A, CCCD 098765432101, phone 0912345678",
    # Edge cases
    "",                          # Empty
    "Just a normal question",    # No PII
    "A" * 5000,                  # Very long
    "Lý Văn Bình ở 123 Lê Lợi", # Vietnamese name (Presidio EN may miss)
    "tax_code:0123456789-001 cccd:012345678901",  # Multiple PII
]


def detect_pii_found(original, redacted):
    """Check if any PII was detected and redacted."""
    if original == redacted:
        return "None"
    
    pii_types = []
    for pii_type in VN_PII.keys():
        if f"[{pii_type.upper()}]" in redacted:
            pii_types.append(pii_type.upper())
    
    # Check for Presidio entities
    if "<" in redacted and ">" in redacted:
        pii_types.append("PRESIDIO_ENTITY")
    
    return ", ".join(pii_types) if pii_types else "Unknown"


if __name__ == "__main__":
    print("=" * 60)
    print("Task C.1 — Input Guardrail: PII Redaction")
    print("=" * 60)
    print()
    
    # Initialize guard
    print("Initializing InputGuard (Presidio + VN regex)...")
    guard = InputGuard()
    print("✓ Guard initialized")
    print()
    
    # Test all inputs
    results = []
    latencies = []
    
    print(f"Testing {len(test_inputs)} inputs...")
    print()
    
    for i, text in enumerate(test_inputs, 1):
        display_text = text[:50] + "..." if len(text) > 50 else text
        print(f"[{i}/{len(test_inputs)}] Testing: {display_text}")
        
        try:
            output, latency_ms = guard.sanitize(text)
            pii_found = detect_pii_found(text, output)
            
            results.append({
                'input': text[:100],  # Truncate for CSV
                'output': output[:100],
                'pii_found': pii_found,
                'latency_ms': round(latency_ms, 2)
            })
            latencies.append(latency_ms)
            
            print(f"  → PII found: {pii_found}")
            print(f"  → Latency: {latency_ms:.2f}ms")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'input': text[:100],
                'output': f"ERROR: {str(e)}",
                'pii_found': "ERROR",
                'latency_ms': 0
            })
        print()
    
    # Save results
    output_dir = Path("results/phase_c")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(results)
    output_file = output_dir / "pii_test_results.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("=" * 60)
    print("Results Summary")
    print("=" * 60)
    print()
    
    # Detection rate
    pii_detected = sum(1 for r in results if r['pii_found'] != "None" and r['pii_found'] != "ERROR")
    # Exclude edge cases (empty, no PII, very long)
    expected_pii_count = 7  # First 5 + last 1 have PII
    detection_rate = (pii_detected / expected_pii_count) * 100
    
    print(f"Detection rate: {pii_detected}/{expected_pii_count} = {detection_rate:.1f}%")
    print(f"  Target: ≥ 80%")
    print(f"  Status: {'✓ PASS' if detection_rate >= 80 else '✗ FAIL'}")
    print()
    
    # Latency stats
    import numpy as np
    valid_latencies = [l for l in latencies if l > 0]
    if valid_latencies:
        p50 = np.percentile(valid_latencies, 50)
        p95 = np.percentile(valid_latencies, 95)
        p99 = np.percentile(valid_latencies, 99)
        
        print(f"Latency statistics:")
        print(f"  P50: {p50:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        print(f"  Target P95: < 50ms")
        print(f"  Status: {'✓ PASS' if p95 < 50 else '✗ FAIL'}")
    print()
    
    print(f"✓ Saved results to: {output_file}")
    print()
    
    print("=" * 60)
    print("✓ Task C.1 Complete!")
    print("=" * 60)
    print()
    print("Next: Task C.2 - Topic Scope Validator")
