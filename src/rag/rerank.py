"""Reranking module - Cross-encoder - copied from Day-18"""

from dataclasses import dataclass
from src.rag.config import RERANK_TOP_K


@dataclass
class RerankResult:
    text: str
    original_score: float
    rerank_score: float
    metadata: dict
    rank: int


class CrossEncoderReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from FlagEmbedding import FlagReranker
                self._model = FlagReranker(self.model_name, use_fp16=True)
            except Exception:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
        return self._model

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        """Rerank documents: top-20 → top-k"""
        if not documents:
            return []

        model = self._load_model()
        pairs = [(query, d.get("text", "")) for d in documents]

        scores = None
        if hasattr(model, "compute_score"):
            scores = model.compute_score(pairs)
        elif hasattr(model, "predict"):
            scores = model.predict(pairs)
        else:
            raise RuntimeError("Unsupported reranker model interface")

        scored_docs = list(zip(scores, documents))
        scored_docs.sort(key=lambda x: float(x[0]), reverse=True)
        scored_docs = scored_docs[:top_k]

        results: list[RerankResult] = []
        for i, (s, d) in enumerate(scored_docs, start=1):
            results.append(
                RerankResult(
                    text=d.get("text", ""),
                    original_score=float(d.get("score", 0.0)),
                    rerank_score=float(s),
                    metadata=d.get("metadata", {}),
                    rank=i,
                )
            )
        return results
