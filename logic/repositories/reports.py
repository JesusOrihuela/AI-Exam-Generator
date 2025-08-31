# logic/repositories/reports.py
import json
from typing import Dict, Any
from utils.paths import REPORTED_QUESTIONS_FILE


def append_report(record: Dict[str, Any]) -> bool:
    try:
        with open(REPORTED_QUESTIONS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False
