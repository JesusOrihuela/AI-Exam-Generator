# logic/analyzer/assembler.py
from __future__ import annotations
from typing import List


def assemble_final_summary(block_summaries: List[str]) -> str:
    """
    Une resúmenes de bloque en un texto final legible, usando separadores.
    """
    cleaned = [s.strip() for s in block_summaries if s and s.strip()]
    return "\n\n---\n\n".join(cleaned)
