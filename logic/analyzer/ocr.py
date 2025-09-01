# logic/analyzer/ocr.py
from __future__ import annotations
import base64
from typing import List, Dict, Any, Optional

from config import OCR_MODE, OCR_ENABLED, OCR_LANG, OCR_TEXT_MAX_CHARS, OCR_TOKEN_ESTIMATE
from openai import OpenAI


def _pytesseract_available() -> bool:
    try:
        import pytesseract  # noqa
        return True
    except Exception:
        return False


def _ocr_local(image_bytes: bytes, lang: str = OCR_LANG) -> Optional[str]:
    try:
        import pytesseract
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(image_bytes))
        txt = pytesseract.image_to_string(im, lang=lang) or ""
        return txt.strip()
    except Exception:
        return None


def _ocr_llm(client: OpenAI, data_url: str) -> Optional[str]:
    try:
        # Petición mínima al modelo visión para transcribir texto lo más fiel posible.
        messages = [
            {"role": "system", "content": "Transcribe exactamente todo el texto visible en la imagen. No agregues comentarios. Devuelve solo el texto crudo."},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": data_url}}]},
        ]
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.0,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return None


def _data_url_to_bytes(data_url: str) -> Optional[bytes]:
    try:
        header, b64 = data_url.split(",", 1)
        return base64.b64decode(b64)
    except Exception:
        return None


def apply_ocr_to_items(items: List[Dict[str, Any]], client: OpenAI | None, allow_fn) -> None:
    """
    Enriquecer items de imagen con campo 'ocr' si OCR está habilitado.
    - Usa OCR local (tesseract) cuando está disponible y OCR_MODE lo permite.
    - Si no, usa OCR vía LLM (requiere client). La función `allow_fn(tokens)` debe
      respetar el presupuesto (TPM/RPM) cuando se use el modo LLM.
    Nota: modifica 'items' in-place.
    """
    if not OCR_ENABLED:
        return

    use_local = (OCR_MODE in ("auto", "local")) and _pytesseract_available()
    use_llm = (OCR_MODE in ("auto", "llm")) and client is not None

    for it in items:
        if it.get("kind") != "image":
            continue
        if it.get("ocr"):
            continue  # ya tiene ocr

        data_url = it.get("data_url")
        if not data_url:
            continue

        text: Optional[str] = None
        if use_local:
            raw = _data_url_to_bytes(data_url)
            if raw:
                text = _ocr_local(raw, lang=OCR_LANG)

        if (not text) and use_llm:
            # respeta presupuesto estimado
            allow_fn(OCR_TOKEN_ESTIMATE)
            text = _ocr_llm(client, data_url)

        if text:
            it["ocr"] = text[:OCR_TEXT_MAX_CHARS]
