"""Chunking module - copied from Day-18"""

import os
import glob
import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    metadata: dict = field(default_factory=dict)
    parent_id: str | None = None


def load_documents(data_dir: str) -> list[dict]:
    """Load all markdown/text files from directory"""
    docs = []
    patterns = ["*.md", "*.txt"]
    for pattern in patterns:
        for fp in sorted(glob.glob(os.path.join(data_dir, pattern))):
            with open(fp, encoding="utf-8") as f:
                docs.append({"text": f.read(), "metadata": {"source": os.path.basename(fp)}})
    return docs


def chunk_hierarchical(text: str, parent_size: int = 2048,
                       child_size: int = 256,
                       metadata: dict | None = None) -> tuple[list[Chunk], list[Chunk]]:
    """
    Parent-child hierarchy chunking
    
    Returns:
        (parents, children) — each child has parent_id link to parent
    """
    metadata = metadata or {}
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    parents: list[Chunk] = []
    children: list[Chunk] = []

    current_text = ""
    for para in paragraphs:
        if len(current_text) + len(para) > parent_size and current_text:
            pid = f"parent_{len(parents)}"
            parents.append(Chunk(
                text=current_text.strip(),
                metadata={**metadata, "chunk_type": "parent", "parent_id": pid},
            ))
            current_text = ""
        current_text += para + "\n\n"
    
    if current_text.strip():
        pid = f"parent_{len(parents)}"
        parents.append(Chunk(
            text=current_text.strip(),
            metadata={**metadata, "chunk_type": "parent", "parent_id": pid},
        ))

    # Create children from parents
    for parent in parents:
        pid = parent.metadata["parent_id"]
        p_text = parent.text
        start = 0
        while start < len(p_text):
            child_text = p_text[start:start + child_size]
            children.append(Chunk(
                text=child_text,
                metadata={**metadata, "chunk_type": "child"},
                parent_id=pid,
            ))
            start += child_size

    return parents, children
