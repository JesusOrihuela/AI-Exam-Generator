import os
import traceback
from PyQt6.QtCore import QThread, pyqtSignal
from openai import APIConnectionError, RateLimitError, AuthenticationError, BadRequestError, InternalServerError
from .document_processor import DocumentProcessor
from .exam_generator import ExamGenerator

class ProcessingWorker(QThread):
    """
    Worker para la FASE 1: Procesa archivos crudos y genera un resumen consolidado.
    Implementa la estrategia Map-Reduce.
    """
    finished = pyqtSignal(str, list)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, api_key, file_paths):
        super().__init__()
        self.api_key = api_key
        self.file_paths = file_paths

    def run(self):
        try:
            self.progress.emit("Paso 1/4: Procesando documentos...")
            processor = DocumentProcessor()
            content = processor.process_files(self.file_paths)
            if not content:
                self.error.emit("No se pudo extraer contenido de los documentos."); return
            
            chunks = processor.chunk_content(content)
            if not chunks:
                self.error.emit("El contenido extraído parece estar vacío."); return
            
            generator = ExamGenerator(self.api_key)
            summaries = []

            self.progress.emit(f"Paso 2/4: Analizando {len(chunks)} fragmento(s)...")
            for i, chunk in enumerate(chunks):
                self.progress.emit(f"Paso 2/4: Analizando fragmento {i + 1}/{len(chunks)}...")
                summary = generator.get_summary_from_chunk(chunk)
                summaries.append(summary)

            self.progress.emit("Paso 3/4: Consolidando información...")
            final_summary = "\n\n---\n\n".join(summaries)
            
            self.progress.emit("Paso 4/4: Análisis completado.")
            filenames = [os.path.basename(p) for p in self.file_paths]
            self.finished.emit(final_summary, filenames)

        except AuthenticationError as e:
            self.error.emit(f"Error de Autenticación: La API Key de OpenAI es inválida o ha expirado. Detalle: {e}")
        except RateLimitError as e:
            self.error.emit(f"Error de Límite de Tasa: Has excedido tu cuota de uso de la API. Detalle: {e}")
        except APIConnectionError as e:
            self.error.emit(f"Error de Conexión: No se pudo establecer comunicación con los servidores de OpenAI. Detalle: {e}")
        except BadRequestError as e:
            api_detail_message = str(e)
            try:
                if hasattr(e, 'response') and hasattr(e.response, 'json') and callable(e.response.json):
                    response_json = e.response.json()
                    if 'error' in response_json and 'message' in response_json['error']:
                        api_detail_message = response_json['error']['message']
            except Exception:
                pass
            
            error_message = f"Error de Solicitud: La API rechazó la petición. Detalle: {api_detail_message}"
            if "context_length_exceeded" in api_detail_message:
                error_message = f"Error de Solicitud: El contenido de los documentos es demasiado grande y excede el límite de tokens del modelo. Considere reducir el tamaño de los documentos o el número de preguntas. (Detalle: {api_detail_message})"
            self.error.emit(error_message)
        except InternalServerError as e:
            self.error.emit(f"Error Interno del Servidor: OpenAI está experimentando problemas. Por favor, inténtalo de nuevo más tarde. Detalle: {e}")
        except ValueError as e:
            self.error.emit(f"Error de Datos: {str(e)}")
        except Exception as e:
            print(f"ERROR INESPERADO EN PROCESSING WORKER:\n{traceback.format_exc()}")
            self.error.emit(f"Ha ocurrido un error inesperado al procesar el contenido: {str(e)}. Consulta la consola para más detalles técnicos.")

class ExamGenerationWorker(QThread):
    """
    Worker para la FASE 2: Genera un examen a partir de un resumen ya procesado.
    Implementa el sub-chunking del resumen si es demasiado grande.
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
                self.progress.emit(f"Resumen consolidado muy grande ({len(self.summary_context)} chars). Dividiendo para generar examen...")
                summary_chunks = generator._split_summary_text(self.summary_context, MAX_SUMMARY_CHARS_FOR_GEN)
                
                questions_per_chunk = self.num_questions // len(summary_chunks)
                remainder_questions = self.num_questions % len(summary_chunks)

                for i, chunk_part in enumerate(summary_chunks):
                    current_questions_count = questions_per_chunk + (1 if i < remainder_questions else 0)
                    if current_questions_count == 0: continue

                    self.progress.emit(f"Generando {current_questions_count} preguntas del fragmento {i + 1}/{len(summary_chunks)} del resumen...")
                    part_questions = generator.generate_exam_from_summary_part(
                        chunk_part, current_questions_count, self.temperature, self.top_p
                    )
                    all_questions.extend(part_questions)
            else:
                self.progress.emit("Generando preguntas desde el contenido analizado (resumen completo)...")
                all_questions = generator.generate_exam_from_summary_part(
                    self.summary_context, self.num_questions, self.temperature, self.top_p
                )
            
            self.progress.emit("Examen generado con éxito.")
            self.finished.emit(all_questions)

        except AuthenticationError as e:
            self.error.emit(f"Error de Autenticación: La API Key de OpenAI es inválida o ha expirado. Detalle: {e}")
        except RateLimitError as e:
            self.error.emit(f"Error de Límite de Tasa: Has excedido tu cuota de uso de la API. Detalle: {e}")
        except APIConnectionError as e:
            self.error.emit(f"Error de Conexión: No se pudo establecer comunicación con los servidores de OpenAI. Detalle: {e}")
        except BadRequestError as e:
            api_detail_message = str(e)
            try:
                if hasattr(e, 'response') and hasattr(e.response, 'json') and callable(e.response.json):
                    response_json = e.response.json()
                    if 'error' in response_json and 'message' in response_json['error']:
                        api_detail_message = response_json['error']['message']
            except Exception:
                pass
            
            error_message = f"Error de Solicitud: La API rechazó la petición. Detalle: {api_detail_message}"
            if "context_length_exceeded" in api_detail_message:
                error_message = f"Error de Solicitud: El fragmento del resumen es demasiado grande y excede el límite de tokens del modelo. Intenta reducir el número total de preguntas solicitadas o el tamaño de los documentos originales. (Detalle: {api_detail_message})"
            self.error.emit(error_message)
        except InternalServerError as e:
            self.error.emit(f"Error Interno del Servidor: OpenAI está experimentando problemas. Por favor, inténtalo de nuevo más tarde. Detalle: {e}")
        except ValueError as e:
            self.error.emit(f"Error de Datos: {str(e)}")
        except Exception as e:
            print(f"ERROR INESPERADO EN EXAM GENERATION WORKER:\n{traceback.format_exc()}")
            self.error.emit(f"Ha ocurrido un error inesperado al generar el examen: {str(e)}. Consulta la consola para más detalles técnicos.")