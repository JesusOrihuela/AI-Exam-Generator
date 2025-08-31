import json
from typing import List
from config import MODEL_SUMMARY, MODEL_EXAM
from logic.llm_client import make_client
from logic.prompts import SUMMARY_SYSTEM_PROMPT, exam_system_prompt


class ExamGenerator:
    """Interactúa con la API de OpenAI para resumir fragmentos y generar exámenes."""

    def __init__(self, api_key):
        self.client = make_client(api_key=api_key)
        # Modelos definidos en config (mismo valor que antes)
        self.model_summary = MODEL_SUMMARY
        self.model_exam = MODEL_EXAM

    @staticmethod
    def _split_summary_text(summary_text: str, max_chars_per_chunk: int = 70000) -> List[str]:
        """Divide un resumen largo en fragmentos manejables."""
        chunks = []
        if not summary_text:
            return chunks

        sections = summary_text.split('\n\n---\n\n')
        current_chunk_parts = []
        current_chunk_len = 0

        for section in sections:
            section_len = len(section)
            if current_chunk_len + section_len + len('\n\n---\n\n') > max_chars_per_chunk and current_chunk_parts:
                chunks.append('\n\n---\n\n'.join(current_chunk_parts))
                current_chunk_parts = []
                current_chunk_len = 0

            current_chunk_parts.append(section)
            current_chunk_len += section_len + len('\n\n---\n\n')

        if current_chunk_parts:
            chunks.append('\n\n---\n\n'.join(current_chunk_parts))

        final_chunks = []
        if not chunks or any(len(c) > max_chars_per_chunk for c in chunks):
            for chunk_part in chunks if chunks else [summary_text]:
                for i in range(0, len(chunk_part), max_chars_per_chunk):
                    final_chunks.append(chunk_part[i:i + max_chars_per_chunk])
        else:
            final_chunks = chunks

        return final_chunks

    def get_summary_from_chunk(self, chunk_content):
        """Extrae conceptos clave de un fragmento usando el modelo de resumen."""
        system_prompt = SUMMARY_SYSTEM_PROMPT
        user_message_content = [{"type": "text", "text": "Sintetiza los puntos clave del siguiente contenido:"}]
        user_message_content.extend(chunk_content)

        response = self.client.chat.completions.create(
            model=self.model_summary,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message_content}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content

    def generate_exam_from_summary_part(self, summary_part_context, num_questions_part, temperature, top_p):
        """Genera preguntas a partir de un fragmento de resumen."""
        if not summary_part_context:
            return []

        system_prompt = exam_system_prompt(num_questions_part)

        response = self.client.chat.completions.create(
            model=self.model_exam,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto de Resumen (Parte):\n{summary_part_context}\n\nGenera exactamente {num_questions_part} preguntas."}
            ],
            temperature=temperature,
            top_p=top_p,
            response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content

        try:
            json_response = json.loads(response_text)
        except json.JSONDecodeError:
            raise ValueError("La API devolvió una respuesta JSON inválida al generar preguntas.")

        if "preguntas" in json_response and isinstance(json_response["preguntas"], list):
            fixed_questions = []
            for i in range(num_questions_part):
                if i < len(json_response["preguntas"]):
                    q = json_response["preguntas"][i]
                    fixed_questions.append({
                        "pregunta": q.get("pregunta", f"Pregunta {i+1} no disponible."),
                        "opciones": q.get("opciones", ["", "", ""]),
                        "respuesta_correcta": q.get("respuesta_correcta", ""),
                        "justificacion": q.get("justificacion", "No se generó justificación.")
                    })
                else:
                    fixed_questions.append({
                        "pregunta": f"Pregunta {i+1} no disponible.",
                        "opciones": ["", "", ""],
                        "respuesta_correcta": "",
                        "justificacion": "No se generó justificación."
                    })
            return fixed_questions
        else:
            raise ValueError("La respuesta de la API no contiene una clave 'preguntas' con una lista.")
