"""Search module - Hybrid BM25 + Dense - copied from Day-18"""

from dataclasses import dataclass
from src.rag.config import (
    QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME,
    EMBEDDING_MODEL, EMBEDDING_DIM,
    BM25_TOP_K, DENSE_TOP_K, HYBRID_TOP_K
)


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict
    method: str  # "bm25", "dense", "hybrid"


def segment_vietnamese(text: str) -> str:
    """Segment Vietnamese text into words"""
    try:
        from underthesea import word_tokenize
        return word_tokenize(text, format="text")
    except ImportError:
        pass
    return text  # fallback


class BM25Search:
    def __init__(self):
        self.corpus_tokens = []
        self.documents = []
        self.bm25 = None

    def index(self, chunks: list[dict]) -> None:
        """Build BM25 index from chunks"""
        self.documents = chunks
        self.corpus_tokens = []
        punct = ".,;:!?\"'()"
        
        for chunk in chunks:
            seg = segment_vietnamese(chunk["text"]).lower().split()
            tokens = []
            for t in seg:
                t = t.strip(punct).strip('"').strip("'")
                if t:
                    tokens.append(t)
            self.corpus_tokens.append(tokens)
        
        from rank_bm25 import BM25Okapi
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    def search(self, query: str, top_k: int = BM25_TOP_K) -> list[SearchResult]:
        """Search using BM25"""
        if self.bm25 is None or not self.documents:
            return []
        
        tokenized_query = segment_vietnamese(query).lower().split()
        punct = ".,;:!?\"'()"
        tokenized_query = [t.strip(punct).strip('"').strip("'") for t in tokenized_query if t.strip(punct)]
        
        if not tokenized_query:
            return []
        
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        out = []
        for i in top_indices:
            doc = self.documents[i]
            out.append(SearchResult(
                text=doc["text"],
                score=float(scores[i]),
                metadata=dict(doc.get("metadata", {})),
                method="bm25",
            ))
        return out


class DenseSearch:
    """In-memory dense search using sentence transformers (no Qdrant needed)"""
    def __init__(self):
        self._encoder = None
        self.documents = []
        self.vectors = None

    def _get_encoder(self):
        if self._encoder is None:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer(EMBEDDING_MODEL)
        return self._encoder

    def index(self, chunks: list[dict], collection: str = COLLECTION_NAME) -> None:
        """Index chunks in memory"""
        if not chunks:
            return
        
        self.documents = chunks
        texts = [c["text"] for c in chunks]
        
        print(f"  Encoding {len(texts)} chunks with {EMBEDDING_MODEL}...")
        self.vectors = self._get_encoder().encode(texts, show_progress_bar=False)

    def search(self, query: str, top_k: int = DENSE_TOP_K, collection: str = COLLECTION_NAME) -> list[SearchResult]:
        """Search using dense vectors (in-memory cosine similarity)"""
        if self.vectors is None or len(self.documents) == 0:
            return []
        
        import numpy as np
        
        # Encode query
        query_vector = self._get_encoder().encode(query)
        
        # Compute cosine similarity
        similarities = np.dot(self.vectors, query_vector) / (
            np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query_vector)
        )
        
        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        out: list[SearchResult] = []
        for idx in top_indices:
            doc = self.documents[idx]
            out.append(SearchResult(
                text=doc["text"],
                score=float(similarities[idx]),
                metadata=dict(doc.get("metadata", {})),
                method="dense",
            ))
        return out


def reciprocal_rank_fusion(results_list: list[list[SearchResult]], k: int = 60,
                           top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
    """Merge ranked lists using RRF: score(d) = Σ 1/(k + rank)"""
    rrf_scores: dict[str, dict] = {}
    
    for result_list in results_list:
        for rank, result in enumerate(result_list):
            if result.text not in rrf_scores:
                rrf_scores[result.text] = {"score": 0.0, "result": result}
            rrf_scores[result.text]["score"] += 1.0 / (k + rank + 1)
    
    ordered = sorted(rrf_scores.values(), key=lambda e: e["score"], reverse=True)
    merged: list[SearchResult] = []
    
    for entry in ordered[:top_k]:
        r = entry["result"]
        md = dict(r.metadata) if isinstance(r.metadata, dict) else r.metadata
        merged.append(SearchResult(
            text=r.text,
            score=entry["score"],
            metadata=md,
            method="hybrid"
        ))
    
    return merged


class HybridSearch:
    """Combines BM25 + Dense + RRF"""
    def __init__(self):
        self.bm25 = BM25Search()
        self.dense = DenseSearch()

    def index(self, chunks: list[dict]) -> None:
        self.bm25.index(chunks)
        self.dense.index(chunks)

    def search(self, query: str, top_k: int = HYBRID_TOP_K) -> list[SearchResult]:
        bm25_results = self.bm25.search(query, top_k=BM25_TOP_K)
        dense_results = self.dense.search(query, top_k=DENSE_TOP_K)
        return reciprocal_rank_fusion([bm25_results, dense_results], top_k=top_k)
