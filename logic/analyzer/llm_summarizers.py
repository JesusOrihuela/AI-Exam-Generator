# logic/analyzer/llm_summarizers.py
from __future__ import annotations
from typing import List, Dict, Any
from openai import OpenAI


SUMMARY_SYSTEM_PROMPT = (
    "Eres un analista experto. A partir del contenido (texto e imágenes) produce un resumen "
    "denso y útil para crear preguntas de evaluación. Extrae hechos verificables, definiciones, "
    "relaciones (causa→efecto, comparación, pasos), y menciona valores/claves si aparecen en figuras. "
    "Evita redundancias y relleno. Devuelve texto claro en español."
)

AGGREGATE_SYSTEM_PROMPT = (
    "Eres un sintetizador. Combina múltiples resúmenes parciales en un único resumen compacto, "
    "eliminando redundancias y manteniendo solo la información más relevante y evaluable. Español."
)


def summarize_block(client: OpenAI, model: str, content: List[Dict[str, Any]], temperature: float = 0.2) -> str:
    """
    Hace una llamada multimodal (texto + image_url) para producir un resumen denso del bloque.
    """
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def aggregate_summaries(client: OpenAI, model: str, partial_summaries: List[str], temperature: float = 0.2) -> str:
    """
    Opcional: comprime una lista de resúmenes parciales en uno solo más corto.
    """
    joined = "\n\n---\n\n".join(partial_summaries)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": AGGREGATE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Combina y comprime estos resúmenes:\n\n{joined}"},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()
