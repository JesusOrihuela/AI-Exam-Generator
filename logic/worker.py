import os
import time
import traceback
from PyQt6.QtCore import QThread, pyqtSignal
from openai import APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, InternalServerError
from .document_processor import DocumentProcessor
from .exam_generator import ExamGenerator


class ProcessingWorker(QThread):
    """
    Worker para la FASE 1: Procesa archivos de manera INDEPENDIENTE
    y genera un resumen por cada uno.
    """
    finished = pyqtSignal(str, str)  # summary, filename
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


class ExamGenerationWorker(QThread):
    """
    Worker para la FASE 2: Genera un examen a partir de un resumen ya procesado.
    Implementa sub-chunking si el resumen es demasiado grande.
    """
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, api_key, summary_context, num_questions, temperature, top_p):
        super().__init__()
        self.api_key = api_key
        self.summary_context = summary_context
        self.num_questions = num_questions
        self.temperature = temperature
        self.top_p = top_p

    def run(self):
        try:
            generator = ExamGenerator(self.api_key)
            all_questions = []

            MAX_SUMMARY_CHARS_FOR_GEN = 70000

            if len(self.summary_context) > MAX_SUMMARY_CHARS_FOR_GEN:
                self.progress.emit("Resumen muy grande. Dividiendo...")
                summary_chunks = generator._split_summary_text(self.summary_context, MAX_SUMMARY_CHARS_FOR_GEN)

                questions_per_chunk = self.num_questions // len(summary_chunks)
                remainder_questions = self.num_questions % len(summary_chunks)

                for i, chunk_part in enumerate(summary_chunks):
                    current_questions_count = questions_per_chunk + (1 if i < remainder_questions else 0)
                    if current_questions_count == 0:
                        continue
                    self.progress.emit(f"Generando {current_questions_count} preguntas del fragmento {i+1}/{len(summary_chunks)}...")
                    part_questions = generator.generate_exam_from_summary_part(
                        chunk_part,
                        current_questions_count,
                        self.temperature,
                        self.top_p
                    )
                    all_questions.extend(part_questions)
                    if i < len(summary_chunks) - 1:
                        time.sleep(1)
            else:
                self.progress.emit("Generando preguntas del resumen completo...")
                all_questions = generator.generate_exam_from_summary_part(
                    self.summary_context,
                    self.num_questions,
                    self.temperature,
                    self.top_p
                )

            self.progress.emit("Examen generado con éxito.")
            self.finished.emit(all_questions)

        except Exception as e:
            print(f"ERROR EN EXAM GENERATION WORKER:\n{traceback.format_exc()}")
            self.error.emit(str(e))
