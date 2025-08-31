# logic/workers/processing.py
import os
import time
import traceback
from PyQt6.QtCore import QThread, pyqtSignal
from openai import APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, InternalServerError

from logic.document_processor import DocumentProcessor
from logic.exam_generator import ExamGenerator


class ProcessingWorker(QThread):
    """
    Worker para la FASE 1: Procesa archivos de manera INDEPENDIENTE
    y genera un resumen por cada uno.
    """
    finished = pyqtSignal(str, str)  # summary, filename (por archivo)
    all_done = pyqtSignal()          # ← NUEVO: emite cuando termina TODO el lote
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, api_key, file_paths):
        super().__init__()
        self.api_key = api_key
        self.file_paths = file_paths

    def run(self):
        try:
            processor = DocumentProcessor()
            generator = ExamGenerator(self.api_key)

            for file_path in self.file_paths:
                filename = os.path.basename(file_path)
                self.progress.emit(f"Procesando documento: {filename}")

                content = processor.process_files([file_path])
                if not content:
                    self.error.emit(f"No se pudo extraer contenido de {filename}.")
                    continue

                chunks = processor.chunk_content(content)
                if not chunks:
                    self.error.emit(f"El documento {filename} parece estar vacío.")
                    continue

                summaries = []
                for i, chunk in enumerate(chunks):
                    self.progress.emit(f"Analizando fragmento {i+1}/{len(chunks)} de {filename}...")
                    summary = generator.get_summary_from_chunk(chunk)
                    summaries.append(summary)
                    if i < len(chunks) - 1:
                        time.sleep(1)  # evitar límites TPM

                final_summary = "\n\n---\n\n".join(summaries)
                self.progress.emit(f"Análisis completado para {filename}.")
                self.finished.emit(final_summary, filename)

                time.sleep(1)  # pausa entre documentos

            # ← NUEVO: avisamos que terminó TODO el lote
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
