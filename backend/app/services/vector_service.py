from __future__ import annotations

import re


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = start + chunk_size
        chunks.append(cleaned[start:end])
        if end >= len(cleaned):
            break
        start = max(end - chunk_overlap, start + 1)
    return chunks


def embed_text(text: str, dimensions: int) -> list[float]:
    vector = [0.0] * dimensions
    for token in tokenize(text):
        vector[hash(token) % dimensions] += 1.0
    magnitude = sum(value * value for value in vector) ** 0.5 or 1.0
    return [round(value / magnitude, 6) for value in vector]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]{2,}", text.lower())
