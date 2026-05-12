"""
Task A.1 — Synthetic Test Set Generation (15 phút) — 8 điểm
Updated for RAGAS 0.4.x API
"""

import asyncio
import sys

# Fix for Windows event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

from ragas.testset import TestsetGenerator
from ragas.testset.synthesizers import default_query_distribution
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

print("Loading documents...")
docs_path = Path("./docs")
documents = []

# Load all text files
for txt_file in docs_path.glob("**/*.txt"):
    try:
        loader = TextLoader(str(txt_file), encoding='utf-8')
        documents.extend(loader.load())
        print(f"  Loaded: {txt_file.name}")
    except Exception as e:
        print(f"  Warning: Could not load {txt_file}: {e}")

# Also load markdown files if any
for md_file in docs_path.glob("**/*.md"):
    try:
        loader = TextLoader(str(md_file), encoding='utf-8')
        documents.extend(loader.load())
        print(f"  Loaded: {md_file.name}")
    except Exception as e:
        print(f"  Warning: Could not load {md_file}: {e}")

print(f"\n✓ Loaded {len(documents)} documents")

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
docs = text_splitter.split_documents(documents)
print(f"Split into {len(docs)} chunks")

# Setup generator with RAGAS 0.4.x API
print("Setting up generator...")
generator_llm = LangchainLLMWrapper(ChatOpenAI(
    model="gpt-4o-mini",
    timeout=120,  # Increase timeout to 120 seconds
    max_retries=3  # Retry on failure
))
embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

generator = TestsetGenerator(
    llm=generator_llm,
    embedding_model=embeddings
)

# Generate test set with default distribution
print("Generating test set (this may take 5-10 minutes)...")
print("Note: If connection drops, the script will retry automatically...")
testset = generator.generate_with_langchain_docs(
    documents=docs,
    testset_size=50,
    query_distribution=default_query_distribution(generator_llm)
)

# Save
import os
os.makedirs("results/phase_a", exist_ok=True)
df = testset.to_pandas()
df.to_csv("results/phase_a/testset_v1.csv", index=False)

print(f"\n✓ Test set generated: {len(df)} questions")
print(f"✓ Saved to: results/phase_a/testset_v1.csv")
print(f"\nColumns: {list(df.columns)}")

# Check distribution if available
if 'query_type' in df.columns:
    print("\nQuery type distribution:")
    print(df['query_type'].value_counts())
elif 'evolution_type' in df.columns:
    print("\nEvolution type distribution:")
    print(df['evolution_type'].value_counts())

