# models.py
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Question:
    pregunta: str
    opciones: List[str]
    respuesta_correcta: str
    justificacion: str


@dataclass
class LibraryItem:
    name: str
    created_at: float
    source_files: List[str]
    summary: str
