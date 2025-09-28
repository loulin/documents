#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple retrieval demo over modular endocrine knowledge CSVs."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

BASE_DIR = Path(__file__).resolve().parent
MODULAR_DIR = BASE_DIR / "modular_endocrine_knowledge"


def iter_documents() -> Iterable[Tuple[int, Dict[str, str]]]:
    doc_id = 0
    for csv_path in sorted(MODULAR_DIR.glob("*.csv")):
        if csv_path.name == "index.csv":
            continue
        with csv_path.open(encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                content = " ".join(
                    filter(
                        None,
                        [
                            row.get("section"),
                            row.get("entity_name"),
                            row.get("entity_type"),
                            row.get("category"),
                            row.get("attribute_path"),
                            row.get("value"),
                        ],
                    )
                )
                if not content.strip():
                    continue
                yield doc_id, {
                    "doc_id": str(doc_id),
                    "section": row.get("section", ""),
                    "entity_id": row.get("entity_id", ""),
                    "entity_name": row.get("entity_name", ""),
                    "attribute_path": row.get("attribute_path", ""),
                    "value": row.get("value", ""),
                    "content": content,
                    "source_file": csv_path.name,
                }
                doc_id += 1


def tokenize(text: str) -> List[str]:
    tokens = []
    current = []
    for ch in text.lower():
        if ch.isalnum() or ch in "_./":
            current.append(ch)
        else:
            if current:
                tokens.append("".join(current))
                current = []
    if current:
        tokens.append("".join(current))
    return tokens


def build_index(documents: Iterable[Tuple[int, Dict[str, str]]]):
    docs: List[Dict[str, str]] = []
    doc_term_counts: List[Counter[str]] = []
    df: Counter[str] = Counter()
    for _, doc in documents:
        docs.append(doc)
        tokens = tokenize(doc["content"])
        counts = Counter(tokens)
        doc_term_counts.append(counts)
        for term in counts:
            df[term] += 1
    total_docs = len(docs)
    idf = {term: math.log((total_docs + 1) / (freq + 1)) + 1 for term, freq in df.items()}
    tfidf_vectors: List[Dict[str, float]] = []
    for counts in doc_term_counts:
        vector = {term: (freq / sum(counts.values())) * idf.get(term, 0.0) for term, freq in counts.items()}
        tfidf_vectors.append(vector)
    return docs, tfidf_vectors, idf


def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    common_terms = set(vec_a) & set(vec_b)
    numerator = sum(vec_a[t] * vec_b[t] for t in common_terms)
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


def search(query: str, docs: List[Dict[str, str]], vectors: List[Dict[str, float]], idf: Dict[str, float], top_k: int = 5):
    query_tokens = tokenize(query)
    counts = Counter(query_tokens)
    query_vector = {term: (freq / sum(counts.values())) * idf.get(term, 0.0) for term, freq in counts.items()}
    scores = []
    for doc, vec in zip(docs, vectors):
        score = cosine_similarity(query_vector, vec)
        if score > 0:
            scores.append((score, doc))
    scores.sort(reverse=True, key=lambda x: x[0])
    return scores[:top_k]


def interactive_loop():
    documents, vectors, idf = build_index(iter_documents())
    print(f"Indexed {len(documents)} knowledge entries. Type 'exit' to quit.")
    while True:
        query = input("Query> ").strip()
        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break
        results = search(query, documents, vectors, idf)
        if not results:
            print("No results found.\n")
            continue
        for rank, (score, doc) in enumerate(results, start=1):
            print(f"[{rank}] score={score:.3f} section={doc['section']} file={doc['source_file']}")
            print(f"    entity: {doc['entity_name']} ({doc['entity_id']})")
            print(f"    path: {doc['attribute_path']}")
            print(f"    value: {doc['value']}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TF-IDF retrieval demo for endocrine knowledge base")
    parser.add_argument("query", nargs="*", help="Optional ad-hoc query (omit for interactive mode)")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to display")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents, vectors, idf = build_index(iter_documents())
    if not documents:
        print("No documents indexed. Please ensure modular CSVs exist.")
        return
    if args.query:
        query = " ".join(args.query)
        results = search(query, documents, vectors, idf, top_k=args.top_k)
        if not results:
            print("No results found.")
            return
        for rank, (score, doc) in enumerate(results, start=1):
            print(f"[{rank}] score={score:.3f} section={doc['section']} file={doc['source_file']}")
            print(f"    entity: {doc['entity_name']} ({doc['entity_id']})")
            print(f"    path: {doc['attribute_path']}")
            print(f"    value: {doc['value']}\n")
    else:
        interactive_loop()


if __name__ == "__main__":
    main()
