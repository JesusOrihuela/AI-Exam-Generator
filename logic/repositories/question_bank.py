# logic/repositories/question_bank.py
import json
from typing import Dict, Any
from utils.paths import QUESTION_BANK_FILE


def load_bank() -> Dict[str, list]:
    try:
        with open(QUESTION_BANK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {}


def save_bank(bank: Dict[str, list]) -> bool:
    try:
        with open(QUESTION_BANK_FILE, "w", encoding="utf-8") as f:
            json.dump(bank, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False
