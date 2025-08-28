import json
from openai import OpenAI
from typing import List

class ExamGenerator:
    """Interactúa con la API de OpenAI para resumir fragmentos y generar exámenes."""
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    @staticmethod
    def _split_summary_text(summary_text: str, max_chars_per_chunk: int = 70000) -> List[str]:
        """
        Divide un texto de resumen grande en fragmentos más pequeños.
        Intenta mantener la coherencia semántica dividiendo por los separadores ya usados.
        """
        chunks = []
        if not summary_text: return chunks

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
        """Toma un fragmento de contenido y extrae sus conceptos clave."""
        system_prompt = """
        Eres un experto en sintetizar información académica y técnica. Tu tarea es analizar el siguiente contenido
        (que puede incluir texto, imágenes interpretadas y fragmentos de código) y extraer los conceptos,
        datos clave, habilidades prácticas evaluables y temas más importantes y únicos.
        Ignora información trivial, repetitiva, o irrelevante para una evaluación de alto nivel.
        Presenta los puntos clave de forma clara, concisa y estructurada en una lista o párrafos.
        Tu objetivo es crear un resumen **denso en información y muy relevante para la creación de preguntas de examen**
        que valoren comprensión y aplicación.
        """
        user_message_content = [{"type": "text", "text": "Sintetiza los puntos clave del siguiente contenido:"}]
        user_message_content.extend(chunk_content)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message_content}],
            temperature=0.2
        )
        return response.choices[0].message.content

    def generate_exam_from_summary_part(self, summary_part_context, num_questions_part, temperature, top_p):
        """Genera una parte de un examen a partir de un fragmento de un resumen consolidado."""
        if not summary_part_context:
            return []

        system_prompt = f"""
        Eres un experto en pedagogía y creación de exámenes objetivos para evaluar comprensión y aplicación.
        Tu tarea es generar **{num_questions_part} preguntas de opción múltiple** en español,
        basadas estrictamente en el "Contexto de Resumen" proporcionado.

        **Especificaciones Clave del Examen:**
        1.  **Tipo de Reactivos:** Exclusivamente preguntas de opción múltiple.
        2.  **Formato:** Cada reactivo debe tener un planteamiento escrito y exactamente tres opciones de respuesta.
        3.  **Correctitud:** Solo una de las tres opciones debe ser la respuesta correcta (clave).
        4.  **Distractores:** Las otras dos opciones deben ser distractores **verosímiles y plausibles**,
            diseñados para detectar errores comunes de interpretación o aplicación del contenido.
            Deben ser similares en estilo y complejidad a la respuesta correcta.
        5.  **Valoración:** Los enunciados deben estar redactados para valorar **conocimientos y habilidades aplicadas**,
            evitando preguntas que solo requieran la memorización de definiciones. Deben exigir interpretación, análisis o resolución.
        6.  **Respuestas Completas:** La opción de respuesta correcta debe **cubrir completamente** lo solicitado en el enunciado. No se aceptan respuestas parcialmente correctas.
        7.  **Estímulos de Apoyo:** Si el "Contexto de Resumen" contiene referencias a estímulos (ej. fragmentos de código, descripciones de imágenes, textos),
            integra preguntas que requieran interpretar o analizar estos estímulos para llegar a la respuesta correcta.
        8.  **Idioma:** Todas las preguntas, opciones y justificaciones deben estar redactadas en español.
        9.  **Redacción de Enunciados:** NO DEBES incluir en el enunciado frases que hagan referencia directa al material fuente, como "según el texto", "en el documento", "como se menciona", "basado en la información proporcionada", o similares. La pregunta debe ser autocontenida y evaluar directamente el contenido, no la capacidad de citar.

        **Formato de Salida JSON:**
        Debes responder con un único objeto JSON que contenga una clave "preguntas",
        cuyo valor sea un array de objetos. Cada objeto de pregunta debe tener las siguientes claves:
        -   "pregunta": El enunciado o problema.
        -   "opciones": Un array de 3 strings, donde el primer elemento es la respuesta correcta y los otros dos son distractores.
        -   "respuesta_correcta": El texto exacto de la opción correcta.
        -   "justificacion": Una explicación concisa de por qué la respuesta correcta es la adecuada.
            **La justificación DEBE COMENZAR con la CITA TEXTUAL DIRECTA del "Contexto de Resumen" entre comillas (`" "`).**
            **A continuación de la cita, DEBE incluir una breve explicación de por qué la opción correcta es la respuesta adecuada y por qué las otras opciones son incorrectas o menos precisas.**
            **NO UTILICES frases introductorias como "La respuesta es correcta porque..." o "Según el resumen..." al inicio de la justificación.**
            **Ejemplo de justificación:**
            `"Las mitocondrias son centrales energéticas de la célula." Esta afirmación del resumen es clave, ya que la función principal de las mitocondrias es producir ATP mediante la respiración celular. Las otras opciones describen funciones de otros orgánulos o procesos celulares.`
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Contexto de Resumen (Parte):\n{summary_part_context}\n\nGenera {num_questions_part} preguntas."}
            ],
            temperature=temperature, top_p=top_p, response_format={"type": "json_object"}
        )
        response_text = response.choices[0].message.content
        
        try: json_response = json.loads(response_text)
        except json.JSONDecodeError: raise ValueError("La API devolvió una respuesta JSON inválida al generar preguntas de una parte del resumen.")

        if "preguntas" in json_response and isinstance(json_response["preguntas"], list):
            return json_response["preguntas"]
        else:
            raise ValueError("La respuesta de la API no contiene una clave 'preguntas' con una lista.")