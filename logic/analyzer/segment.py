# logic/analyzer/segment.py
from __future__ import annotations
from typing import List, Dict, Any
from config import (
    TOKENS_PER_BLOCK_MIN, TOKENS_PER_BLOCK_MAX,
    MAX_IMGS_PER_BLOCK, IMAGE_TOKEN_EQUIV, OCR_TEXT_MAX_CHARS
)


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(text) / 4))  # aproximación


def _item_cost(item: Dict[str, Any]) -> int:
    if item["kind"] == "text":
        return _estimate_tokens(item.get("text", ""))
    # Si el item es imagen y tiene OCR asociado, cuenta su coste textual además del coste base de imagen.
    if item["kind"] == "image":
        cost = IMAGE_TOKEN_EQUIV
        ocr_text = item.get("ocr", "")
        if ocr_text:
            cost += _estimate_tokens(ocr_text[:OCR_TEXT_MAX_CHARS])
        return cost
    return 0


def segment_items_to_blocks(items: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Agrupa items respetando tamaño de tokens y un máximo de imágenes por bloque.
    Las imágenes extra se omiten (no crean bloques nuevos).
    """
    blocks: List[List[Dict[str, Any]]] = []
    current: List[Dict[str, Any]] = []
    current_cost = 0
    current_imgs = 0

    for it in items:
        is_img = it["kind"] == "image"
        if is_img and current_imgs >= MAX_IMGS_PER_BLOCK:
            # omitir imagen extra para evitar explosión
            continue

        cost = _item_cost(it)
        if current and (current_cost + cost > TOKENS_PER_BLOCK_MAX):
            blocks.append(current)
            current = []
            current_cost = 0
            current_imgs = 0

        current.append(it)
        current_cost += cost
        if is_img:
            current_imgs += 1

        if current_cost >= TOKENS_PER_BLOCK_MIN:
            blocks.append(current)
            current = []
            current_cost = 0
            current_imgs = 0

    if current:
        blocks.append(current)

    return blocks


def block_to_chat_content(block: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convierte un bloque a contenido multimodal para Chat:
    - Partes de texto
    - Imágenes (image_url)
    - Texto OCR asociado a cada imagen (si existe), como texto adicional corto.
    """
    content: List[Dict[str, Any]] = []
    for it in block:
        if it["kind"] == "text":
            text = it.get("text", "")
            if text.strip():
                content.append({"type": "text", "text": text})
        else:
            data_url: str = it["data_url"]
            content.append({"type": "image_url", "image_url": {"url": data_url}})
            ocr_text = (it.get("ocr") or "").strip()
            if ocr_text:
                # Añadimos un contexto breve con el OCR (recortado)
                trimmed = ocr_text[:OCR_TEXT_MAX_CHARS]
                content.append({"type": "text", "text": f"Texto detectado en la imagen (OCR):\n{trimmed}"})
    return content


def block_cost_tokens(block: List[Dict[str, Any]]) -> int:
    return sum(_item_cost(it) for it in block)
