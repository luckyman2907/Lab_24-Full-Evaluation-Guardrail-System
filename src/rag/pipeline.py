"""
RAG Pipeline - Main interface for Day-24 evaluation
Provides retrieval + generation functionality

Fix: Reranker (BAAI/bge-reranker-v2-m3) bị lỗi XLMRobertaTokenizer incompatibility
→ Bỏ reranker, dùng top-3 trực tiếp từ HybridSearch
"""

import time
from typing import List, Tuple

# Import from local modules
try:
    from src.rag.chunking import load_documents, chunk_hierarchical
    from src.rag.search import HybridSearch
    from src.rag.config import DATA_DIR, RERANK_TOP_K

    # Build pipeline once at module level
    print("🔧 Building RAG pipeline...")
    start_time = time.time()

    # Load and chunk documents
    docs = load_documents(DATA_DIR)
    all_chunks = []
    for doc in docs:
        parents, children = chunk_hierarchical(doc["text"], metadata=doc["metadata"])
        for child in children:
            all_chunks.append({
                "text": child.text,
                "metadata": {**child.metadata, "parent_id": child.parent_id}
            })

    # Index
    search_engine = HybridSearch()
    search_engine.index(all_chunks)

    build_time = time.time() - start_time
    print(f"✓ Pipeline built in {build_time:.2f}s")
    print(f"  - Loaded {len(docs)} documents")
    print(f"  - Created {len(all_chunks)} chunks")
    print(f"  - Reranker: DISABLED (XLMRobertaTokenizer incompatibility)")
    print(f"  - Using top-{RERANK_TOP_K} from HybridSearch instead")

    RAG_AVAILABLE = True

except Exception as e:
    print(f"⚠ Warning: Could not build RAG pipeline: {e}")
    print("Using demo pipeline instead.")
    search_engine = None
    RAG_AVAILABLE = False


def rag_pipeline(question: str) -> Tuple[str, List[str]]:
    """
    Main RAG pipeline function for Day-24 evaluation

    Args:
        question: User question

    Returns:
        (answer, contexts): Generated answer and list of context strings
    """
    if not RAG_AVAILABLE:
        raise RuntimeError("RAG pipeline not available — check startup errors above")

    # Step 1: Retrieve + rank bằng HybridSearch (BM25 + Dense + RRF)
    results = search_engine.search(question, top_k=RERANK_TOP_K)

    # Step 2: Extract contexts (top-3)
    contexts = [r.text for r in results]

    # Step 3: Generate answer
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    context_str = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(contexts)])

    prompt = f"""Answer the question based on the provided contexts.
Be concise and accurate. If the contexts don't contain enough information, say so.

Contexts:
{context_str}

Question: {question}

Answer:"""

    response = llm.invoke(prompt)
    answer = response.content

    return answer, contexts
