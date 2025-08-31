# utils/paths.py
import os

# Raíz del proyecto = padre de /utils
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

CONTENT_LIBRARY_DIR = os.path.join(PROJECT_ROOT, "content_library")
EXAMS_DIR = os.path.join(PROJECT_ROOT, "exams")

QUESTION_BANK_FILE = os.path.join(PROJECT_ROOT, "question_bank.json")
REPORTED_QUESTIONS_FILE = os.path.join(PROJECT_ROOT, "reported_questions.jsonl")


def ensure_dirs():
    """Crea directorios que la app necesita en tiempo de ejecución (idempotente)."""
    for p in (CONTENT_LIBRARY_DIR, EXAMS_DIR):
        os.makedirs(p, exist_ok=True)
