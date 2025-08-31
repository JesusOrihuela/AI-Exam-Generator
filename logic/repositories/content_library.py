# logic/repositories/content_library.py
import os
import json
import time
from typing import List, Dict, Any
from utils.paths import CONTENT_LIBRARY_DIR


def _safe_filename(name: str) -> str:
    return f"{int(time.time())}_{''.join(filter(str.isalnum, name))}.json"


def list_items() -> List[Dict[str, Any]]:
    """Devuelve una lista de dicts con el contenido de la biblioteca. 
    Adjunta '_file_path' en cada item para poder eliminarlo después.
    """
    os.makedirs(CONTENT_LIBRARY_DIR, exist_ok=True)
    items = []
    for filename in os.listdir(CONTENT_LIBRARY_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(CONTENT_LIBRARY_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                data["_file_path"] = path
                items.append(data)
        except Exception:
            # omitir archivos corruptos
            continue
    return items


def save_item(name: str, source_files: list, summary: str) -> str:
    """Guarda un item en la biblioteca y devuelve la ruta del archivo generado."""
    os.makedirs(CONTENT_LIBRARY_DIR, exist_ok=True)
    content_data = {
        "name": name,
        "source_files": source_files,
        "created_at": time.time(),
        "summary": summary,
    }
    filename = _safe_filename(name)
    path = os.path.join(CONTENT_LIBRARY_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content_data, f, indent=4, ensure_ascii=False)
    return path


def delete_item_by_path(file_path: str) -> bool:
    """Elimina el archivo indicado. Devuelve True si lo elimina, False si no existía."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
