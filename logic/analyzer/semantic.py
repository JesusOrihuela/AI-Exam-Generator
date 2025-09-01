# logic/analyzer/semantic.py
from __future__ import annotations
import re
from typing import List, Dict, Any

from openai import OpenAI
from config import (
    SEMANTIC_SPLIT_ENABLED, EMBEDDINGS_MODEL,
    SEMANTIC_SIM_THRESHOLD, SEMANTIC_MIN_TOKENS,
    SEMANTIC_TARGET_TOKENS, SEMANTIC_MAX_SENTENCES,
    TOKENS_PER_BLOCK_MAX
)


_SENTENCE_RE = re.compile(r'(?<=[\.\!\?])\s+(?=[A-ZÁÉÍÓÚÑÜ0-9])')


def _approx_tokens(s: str) -> int:
    return max(1, int(len(s) / 4))


def _cosine(a: List[float], b: List[float]) -> float:
    import math
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _embed_sentences(client: OpenAI, sentences: List[str]) -> List[List[float]]:
    resp = client.embeddings.create(
        model=EMBEDDINGS_MODEL,
        input=sentences
    )
    return [d.embedding for d in resp.data]


def _split_text_semantically(text: str, client: OpenAI) -> List[str]:
    """
    Divide un texto largo en chunks semánticos (por tema), respetando
    un objetivo de tokens y un mínimo para cerrar el chunk.
    """
    if _approx_tokens(text) <= 2 * TOKENS_PER_BLOCK_MAX:
        return [text]

    # Separación sencilla por oraciones
    sentences = _SENTENCE_RE.split(text.strip())
    if len(sentences) > SEMANTIC_MAX_SENTENCES:
        sentences = sentences[:SEMANTIC_MAX_SENTENCES]

    if not sentences:
        return [text]

    embs = _embed_sentences(client, sentences)

    chunks: List[str] = []
    current: List[str] = [sentences[0]]
    current_tokens = _approx_tokens(sentences[0])
    last_emb = embs[0]

    for s, e in zip(sentences[1:], embs[1:]):
        sim = _cosine(last_emb, e)
        s_tokens = _approx_tokens(s)

        should_split = (
            (sim < SEMANTIC_SIM_THRESHOLD and current_tokens >= SEMANTIC_MIN_TOKENS) or
            (current_tokens + s_tokens > SEMANTIC_TARGET_TOKENS)
        )

        if should_split:
            chunks.append(" ".join(current))
            current = [s]
            current_tokens = s_tokens
        else:
            current.append(s)
            current_tokens += s_tokens

        last_emb = e

    if current:
        chunks.append(" ".join(current))

    return chunks


def apply_semantic_split(items: List[Dict[str, Any]], client: OpenAI) -> List[Dict[str, Any]]:
    """
    Recorre los items; cuando encuentra un item de texto muy largo,
    lo divide en varios items de texto más cortos y cohesionados por tema.
    Mantiene el orden y no toca los items de imagen.
    """
    if not SEMANTIC_SPLIT_ENABLED:
        return items

    out: List[Dict[str, Any]] = []
    for it in items:
        if it.get("kind") != "text":
            out.append(it)
            continue

        text = it.get("text") or ""
        if _approx_tokens(text) <= 2 * TOKENS_PER_BLOCK_MAX:
            out.append(it)
            continue

        parts = _split_text_semantically(text, client)
        for p in parts:
            out.append({"kind": "text", "text": p, "page": it.get("page", 1)})

    return out
