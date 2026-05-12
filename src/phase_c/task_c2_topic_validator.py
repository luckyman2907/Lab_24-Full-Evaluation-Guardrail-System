"""
Task C.2 — Input Guardrail: Topic Scope Validator
Implement topic validator using embedding similarity (Option 1 - Basic).
"""

from langchain_openai import OpenAIEmbeddings
import numpy as np
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TopicGuard:
    def __init__(self, allowed_topics: list[str]):
        self.embeddings = OpenAIEmbeddings()
        self.topic_vectors = [
            self.embeddings.embed_query(t) for t in allowed_topics
        ]
        self.topics = allowed_topics

    def check(self, text: str) -> tuple[bool, str]:
        q_vec = self.embeddings.embed_query(text)
        sims = [
            np.dot(q_vec, tv) / (np.linalg.norm(q_vec) * np.linalg.norm(tv))
            for tv in self.topic_vectors
        ]
        max_sim = max(sims)
        best_topic = self.topics[sims.index(max_sim)]
        if max_sim > 0.6:
            return True, f"On topic: {best_topic}"
        return False, f"Off topic. Closest: {best_topic} ({max_sim:.2f})"


# Test set: 20 inputs (10 on-topic, 10 off-topic)
# Assuming allowed topics are related to Vietnamese land law
test_inputs = [
    # On-topic (10)
    {"text": "Quy định về chuyển nhượng quyền sử dụng đất là gì?", "expected": True},
    {"text": "Thủ tục cấp giấy chứng nhận quyền sử dụng đất như thế nào?", "expected": True},
    {"text": "Ai có quyền sử dụng đất theo Luật Đất đai?", "expected": True},
    {"text": "Thời hạn sử dụng đất ở là bao lâu?", "expected": True},
    {"text": "Điều kiện để được giao đất, cho thuê đất?", "expected": True},
    {"text": "Quy định về bồi thường khi Nhà nước thu hồi đất?", "expected": True},
    {"text": "Các loại đất theo quy định của pháp luật?", "expected": True},
    {"text": "Nghĩa vụ tài chính khi sử dụng đất là gì?", "expected": True},
    {"text": "Quyền và nghĩa vụ của người sử dụng đất?", "expected": True},
    {"text": "Thủ tục đăng ký biến động đất đai?", "expected": True},
    
    # Off-topic (10)
    {"text": "Công thức tính diện tích hình tròn là gì?", "expected": False},
    {"text": "Cách nấu phở bò ngon nhất?", "expected": False},
    {"text": "Lịch sử Chiến tranh thế giới thứ 2?", "expected": False},
    {"text": "Cách cài đặt Python trên Windows?", "expected": False},
    {"text": "Đội tuyển bóng đá Việt Nam thi đấu khi nào?", "expected": False},
    {"text": "Giá vàng hôm nay là bao nhiêu?", "expected": False},
    {"text": "Cách chăm sóc cây lan hồ điệp?", "expected": False},
    {"text": "Thời tiết Hà Nội tuần này như thế nào?", "expected": False},
    {"text": "Cách học tiếng Anh hiệu quả?", "expected": False},
    {"text": "Công nghệ AI sẽ phát triển ra sao?", "expected": False},
]


if __name__ == "__main__":
    print("=" * 60)
    print("Task C.2 — Input Guardrail: Topic Scope Validator")
    print("=" * 60)
    print()
    
    # Define allowed topics (Vietnamese land law domain)
    allowed_topics = [
        "Quyền sử dụng đất",
        "Chuyển nhượng đất đai",
        "Giấy chứng nhận quyền sử dụng đất",
        "Thu hồi đất và bồi thường",
        "Nghĩa vụ tài chính về đất đai",
        "Thủ tục hành chính đất đai",
    ]
    
    print(f"Allowed topics: {len(allowed_topics)}")
    for i, topic in enumerate(allowed_topics, 1):
        print(f"  {i}. {topic}")
    print()
    
    # Initialize guard
    print("Initializing TopicGuard (embedding similarity)...")
    guard = TopicGuard(allowed_topics)
    print("✓ Guard initialized")
    print()
    
    # Test all inputs
    results = []
    correct = 0
    total = len(test_inputs)
    
    print(f"Testing {total} inputs...")
    print()
    
    for i, item in enumerate(test_inputs, 1):
        text = item["text"]
        expected = item["expected"]
        
        display_text = text[:60] + "..." if len(text) > 60 else text
        print(f"[{i}/{total}] {display_text}")
        
        try:
            is_on_topic, reason = guard.check(text)
            is_correct = (is_on_topic == expected)
            
            if is_correct:
                correct += 1
            
            results.append({
                'input': text,
                'expected': 'on-topic' if expected else 'off-topic',
                'actual': 'on-topic' if is_on_topic else 'off-topic',
                'reason': reason,
                'correct': is_correct
            })
            
            status = "✓" if is_correct else "✗"
            print(f"  {status} Expected: {'on-topic' if expected else 'off-topic'}, Got: {'on-topic' if is_on_topic else 'off-topic'}")
            print(f"  → {reason}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'input': text,
                'expected': 'on-topic' if expected else 'off-topic',
                'actual': 'ERROR',
                'reason': str(e),
                'correct': False
            })
        print()
    
    # Save results
    output_dir = Path("results/phase_c")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(results)
    output_file = output_dir / "topic_validation_results.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print("=" * 60)
    print("Results Summary")
    print("=" * 60)
    print()
    
    # Accuracy
    accuracy = (correct / total) * 100
    print(f"Accuracy: {correct}/{total} = {accuracy:.1f}%")
    print(f"  Target: ≥ 75%")
    print(f"  Excellent: ≥ 95%")
    print(f"  Status: {'✓ EXCELLENT' if accuracy >= 95 else '✓ PASS' if accuracy >= 75 else '✗ FAIL'}")
    print()
    
    # Refuse rate (off-topic correctly identified)
    off_topic_items = [r for r in results if r['expected'] == 'off-topic']
    refused = sum(1 for r in off_topic_items if r['actual'] == 'off-topic')
    refuse_rate = (refused / len(off_topic_items)) * 100 if off_topic_items else 0
    
    print(f"Refuse rate (off-topic detection): {refused}/{len(off_topic_items)} = {refuse_rate:.1f}%")
    print()
    
    # False positive rate (on-topic incorrectly rejected)
    on_topic_items = [r for r in results if r['expected'] == 'on-topic']
    false_positives = sum(1 for r in on_topic_items if r['actual'] == 'off-topic')
    fp_rate = (false_positives / len(on_topic_items)) * 100 if on_topic_items else 0
    
    print(f"False positive rate: {false_positives}/{len(on_topic_items)} = {fp_rate:.1f}%")
    print()
    
    print(f"✓ Saved results to: {output_file}")
    print()
    
    # Graceful fallback message example
    print("=" * 60)
    print("Graceful Fallback Message Example")
    print("=" * 60)
    print()
    print("When off-topic detected:")
    print("  'Xin lỗi, câu hỏi của bạn nằm ngoài phạm vi về Luật Đất đai.")
    print("  Tôi chỉ có thể trả lời các câu hỏi liên quan đến:")
    print("  - Quyền sử dụng đất")
    print("  - Chuyển nhượng đất đai")
    print("  - Giấy chứng nhận quyền sử dụng đất")
    print("  - Thu hồi đất và bồi thường")
    print("  - Nghĩa vụ tài chính về đất đai")
    print("  - Thủ tục hành chính đất đai")
    print("  Vui lòng đặt lại câu hỏi liên quan đến các chủ đề trên.'")
    print()
    
    print("=" * 60)
    print("✓ Task C.2 Complete!")
    print("=" * 60)
    print()
    print("Next: Task C.3 - Adversarial Testing")
