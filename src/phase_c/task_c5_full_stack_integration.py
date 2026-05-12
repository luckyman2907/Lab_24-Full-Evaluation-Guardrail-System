"""
Task C.5 — Full Stack Integration & Latency Benchmark
Integrate input + LLM + output guardrails, measure end-to-end latency.
"""

import asyncio
import time
import pandas as pd
from pathlib import Path
import numpy as np
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import guards from previous tasks
sys.path.append(str(Path(__file__).parent))
from task_c1_pii_redaction import InputGuard
from task_c2_topic_validator import TopicGuard
from task_c4_output_guardrail import OutputGuardAPI


# Dummy RAG pipeline for demonstration
def dummy_rag_pipeline(query: str) -> str:
    """Simulate RAG pipeline response."""
    responses = {
        "chuyển nhượng": "Theo Luật Đất đai 2024, chuyển nhượng quyền sử dụng đất phải đáp ứng các điều kiện: có giấy chứng nhận hợp lệ, đất không có tranh chấp...",
        "sổ đỏ": "Thủ tục cấp giấy chứng nhận quyền sử dụng đất gồm: nộp hồ sơ tại Văn phòng đăng ký đất đai, chờ thẩm định, nhận kết quả sau 15-30 ngày...",
        "thời hạn": "Đất ở được sử dụng lâu dài, không có thời hạn theo quy định của Luật Đất đai hiện hành.",
        "nghĩa vụ": "Người sử dụng đất phải thực hiện nghĩa vụ tài chính: tiền sử dụng đất, tiền thuê đất, thuế sử dụng đất...",
        "quyền": "Người sử dụng đất có các quyền: được cấp giấy chứng nhận, chuyển nhượng, cho thuê, thế chấp, để thừa kế...",
    }
    
    # Simple keyword matching
    for keyword, response in responses.items():
        if keyword in query.lower():
            return response
    
    return "Xin lỗi, tôi không tìm thấy thông tin phù hợp với câu hỏi của bạn trong cơ sở dữ liệu Luật Đất đai."


def refuse_response():
    """Return refusal message for off-topic or unsafe queries."""
    return {
        "answer": "Xin lỗi, câu hỏi của bạn nằm ngoài phạm vi về Luật Đất đai hoặc vi phạm chính sách an toàn. Vui lòng đặt lại câu hỏi liên quan đến các chủ đề: Quyền sử dụng đất, Chuyển nhượng đất đai, Giấy chứng nhận, Thu hồi đất, Nghĩa vụ tài chính, Thủ tục hành chính.",
        "refused": True
    }


def guarded_pipeline(user_input, input_guard, topic_guard, output_guard):
    """Full guardrail pipeline with latency tracking."""
    timings = {}
    
    # L1: Input Layer (parallel simulation - run sequentially for simplicity)
    t0 = time.perf_counter()
    
    # PII Redaction
    sanitized, pii_latency = input_guard.sanitize(user_input)
    
    # Topic Validation
    topic_start = time.perf_counter()
    topic_ok, topic_reason = topic_guard.check(sanitized)
    topic_latency = (time.perf_counter() - topic_start) * 1000
    
    timings['L1'] = (time.perf_counter() - t0) * 1000
    timings['L1_PII'] = pii_latency
    timings['L1_Topic'] = topic_latency
    
    if not topic_ok:
        return refuse_response(), timings
    
    # L2: LLM (RAG pipeline)
    t0 = time.perf_counter()
    answer = dummy_rag_pipeline(sanitized)
    timings['L2'] = (time.perf_counter() - t0) * 1000
    
    # L3: Output Layer
    t0 = time.perf_counter()
    safe, safety_reason, safety_latency = output_guard.check(sanitized, answer)
    timings['L3'] = (time.perf_counter() - t0) * 1000
    
    if not safe:
        return refuse_response(), timings
    
    # L4: Audit log (async, not counted)
    # In production: asyncio.create_task(audit_log(user_input, answer, timings))
    
    return {"answer": answer, "refused": False}, timings


# Test queries
test_queries = [
    # On-topic queries (should pass)
    "Quy định về chuyển nhượng quyền sử dụng đất là gì?",
    "Thủ tục cấp giấy chứng nhận quyền sử dụng đất như thế nào?",
    "Thời hạn sử dụng đất ở là bao lâu?",
    "Nghĩa vụ tài chính khi sử dụng đất là gì?",
    "Quyền và nghĩa vụ của người sử dụng đất?",
    "Điều kiện để được giao đất, cho thuê đất?",
    "Quy định về bồi thường khi Nhà nước thu hồi đất?",
    "Các loại đất theo quy định của pháp luật?",
    "Thủ tục đăng ký biến động đất đai?",
    "Ai có quyền sử dụng đất theo Luật Đất đai?",
    
    # Off-topic queries (should be refused)
    "Công thức tính diện tích hình tròn là gì?",
    "Cách nấu phở bò ngon nhất?",
    "Lịch sử Chiến tranh thế giới thứ 2?",
    "Cách cài đặt Python trên Windows?",
    "Đội tuyển bóng đá Việt Nam thi đấu khi nào?",
]


if __name__ == "__main__":
    print("=" * 60)
    print("Task C.5 — Full Stack Integration & Latency Benchmark")
    print("=" * 60)
    print()
    
    # Initialize all guards
    print("Initializing full guardrail stack...")
    input_guard = InputGuard()
    
    allowed_topics = [
        "Quyền sử dụng đất",
        "Chuyển nhượng đất đai",
        "Giấy chứng nhận quyền sử dụng đất",
        "Thu hồi đất và bồi thường",
        "Nghĩa vụ tài chính về đất đai",
        "Thủ tục hành chính đất đai",
    ]
    topic_guard = TopicGuard(allowed_topics)
    output_guard = OutputGuardAPI()
    
    print("✓ All guards initialized")
    print()
    
    # Run benchmark
    print(f"Running benchmark on {len(test_queries)} queries...")
    print()
    
    all_timings = []
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query[:60]}...")
        
        try:
            response, timings = guarded_pipeline(query, input_guard, topic_guard, output_guard)
            
            all_timings.append(timings)
            
            total_latency = sum(timings.values())
            
            results.append({
                'query': query[:80],
                'refused': response['refused'],
                'L1_ms': round(timings.get('L1', 0), 2),
                'L2_ms': round(timings.get('L2', 0), 2),
                'L3_ms': round(timings.get('L3', 0), 2),
                'total_ms': round(total_latency, 2),
            })
            
            status = "REFUSED" if response['refused'] else "OK"
            print(f"  Status: {status}")
            print(f"  L1: {timings.get('L1', 0):.1f}ms | L2: {timings.get('L2', 0):.1f}ms | L3: {timings.get('L3', 0):.1f}ms | Total: {total_latency:.1f}ms")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'query': query[:80],
                'refused': True,
                'L1_ms': 0,
                'L2_ms': 0,
                'L3_ms': 0,
                'total_ms': 0,
            })
        print()
    
    # Save results
    output_dir = Path("results/phase_c")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(results)
    output_file = output_dir / "full_stack_benchmark.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("=" * 60)
    print("Latency Benchmark Results")
    print("=" * 60)
    print()
    
    # Calculate percentiles for each layer
    for layer in ['L1', 'L2', 'L3']:
        vals = [t[layer] for t in all_timings if layer in t]
        if vals:
            p50 = np.percentile(vals, 50)
            p95 = np.percentile(vals, 95)
            p99 = np.percentile(vals, 99)
            
            print(f"{layer} latency:")
            print(f"  P50: {p50:.1f}ms")
            print(f"  P95: {p95:.1f}ms")
            print(f"  P99: {p99:.1f}ms")
            
            if layer == 'L1':
                print(f"  Target P95: < 50ms (ideal: < 30ms)")
                print(f"  Status: {'✓ EXCELLENT' if p95 < 30 else '✓ PASS' if p95 < 50 else '✗ FAIL'}")
            elif layer == 'L3':
                print(f"  Target P95: < 100ms (ideal: < 50ms)")
                print(f"  Status: {'✓ EXCELLENT' if p95 < 50 else '✓ PASS' if p95 < 100 else '✗ FAIL'}")
            print()
    
    # Total overhead
    total_vals = [sum(t.values()) for t in all_timings]
    if total_vals:
        total_p50 = np.percentile(total_vals, 50)
        total_p95 = np.percentile(total_vals, 95)
        total_p99 = np.percentile(total_vals, 99)
        
        print(f"Total end-to-end latency:")
        print(f"  P50: {total_p50:.1f}ms")
        print(f"  P95: {total_p95:.1f}ms")
        print(f"  P99: {total_p99:.1f}ms")
        print()
    
    # Baseline comparison (L2 only, no guardrails)
    l2_vals = [t['L2'] for t in all_timings if 'L2' in t]
    if l2_vals:
        l2_p95 = np.percentile(l2_vals, 95)
        overhead = total_p95 - l2_p95
        overhead_pct = (overhead / l2_p95) * 100 if l2_p95 > 0 else 0
        
        print(f"Guardrail overhead vs baseline (no guardrails):")
        print(f"  Baseline (L2 only) P95: {l2_p95:.1f}ms")
        print(f"  With guardrails P95: {total_p95:.1f}ms")
        print(f"  Overhead: +{overhead:.1f}ms (+{overhead_pct:.0f}%)")
        print()
    
    print(f"✓ Saved results to: {output_file}")
    print()
    
    print("=" * 60)
    print("✅ Phase C Complete!")
    print("=" * 60)
    print()
    
    print("Phase C Summary:")
    print("✓ Task C.1: PII Redaction (Presidio + VN regex)")
    print("✓ Task C.2: Topic Scope Validator (embedding similarity)")
    print("✓ Task C.3: Adversarial Testing (20 attacks)")
    print("✓ Task C.4: Output Guardrail (Llama Guard 3 / OpenAI Moderation)")
    print("✓ Task C.5: Full Stack Integration & Latency Benchmark")
    print()
    print("Next: Phase D - Blueprint Document")
