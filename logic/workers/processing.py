# logic/workers/processing.py
from __future__ import annotations
import os
import time
import traceback
from typing import List

from PyQt6.QtCore import QThread, pyqtSignal
from openai import APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, InternalServerError

from config import MODEL_VISION
from logic.llm_client import make_client
from logic.analyzer.ingest import ingest_files
from logic.analyzer.semantic import apply_semantic_split
from logic.analyzer.ocr import apply_ocr_to_items
from logic.analyzer.segment import segment_items_to_blocks, block_to_chat_content, block_cost_tokens
from logic.analyzer.llm_summarizers import summarize_block, aggregate_summaries
from logic.analyzer.scheduler import RateLimiter
from logic.analyzer.assembler import assemble_final_summary


class ProcessingWorker(QThread):
    """
    Analiza documentos de forma multimodal (texto + imágenes) con segmentación semántica
    y OCR opcional, respetando TPM/RPM. Emite (summary, filename) por cada archivo.
    """
    finished = pyqtSignal(str, str)   # summary, filename
    all_done = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, api_key: str, file_paths: List[str]):
        super().__init__()
        self.api_key = api_key
        self.file_paths = file_paths

    def run(self):
        try:
            client = make_client(self.api_key)
            limiter = RateLimiter()

            for file_path in self.file_paths:
                filename = os.path.basename(file_path)
                self.progress.emit(f"Preparando '{filename}'…")

                # 1) Ingesta (texto + imágenes, sin OCR)
                items = ingest_files([file_path])
                if not items:
                    self.error.emit(f"No se pudo extraer contenido de {filename}.")
                    continue

                # 2) Segmentación semántica previa (solo divide textos largos)
                items = apply_semantic_split(items, client)

                # 3) OCR opcional (local o LLM) sobre imágenes
                #    El limitador se usa solo si se dispara OCR via LLM
                apply_ocr_to_items(items, client, allow_fn=limiter.allow)

                # 4) Empaquetado a bloques (tokens + límite de imágenes/bloque)
                blocks = segment_items_to_blocks(items)
                if not blocks:
                    self.error.emit(f"El documento {filename} parece estar vacío.")
                    continue

                block_summaries: List[str] = []

                # 5) Resumen por bloque (multimodal)
                for i, block in enumerate(blocks, start=1):
                    self.progress.emit(f"Analizando bloque {i}/{len(blocks)} de {filename}…")
                    content = block_to_chat_content(block)
                    est_tokens = block_cost_tokens(block)
                    limiter.allow(est_tokens)

                    summary = summarize_block(
                        client=client,
                        model=MODEL_VISION,
                        content=content,
                        temperature=0.2
                    )
                    block_summaries.append(summary)

                # 6) Agregación opcional
                if len(block_summaries) >= 6:
                    self.progress.emit(f"Compactando resumen de {filename}…")
                    limiter.allow(1200)  # coste estimado
                    final_summary = aggregate_summaries(client, MODEL_VISION, block_summaries)
                else:
                    final_summary = assemble_final_summary(block_summaries)

                self.progress.emit(f"Análisis completado para {filename}.")
                self.finished.emit(final_summary, filename)

                time.sleep(0.5)

            self.all_done.emit()

        except AuthenticationError as e:
            self.error.emit(f"Error de Autenticación: {e}")
        except RateLimitError as e:
            self.error.emit(f"Error de Límite de Tasa: {e}")
        except APIConnectionError as e:
            self.error.emit(f"Error de Conexión: {e}")
        except BadRequestError as e:
            self.error.emit(f"Error de Solicitud: {e}")
        except InternalServerError as e:
            self.error.emit(f"Error Interno del Servidor: {e}")
        except Exception as e:
            print(f"ERROR INESPERADO EN PROCESSING WORKER:\n{traceback.format_exc()}")
            self.error.emit(f"Error inesperado: {str(e)}")
