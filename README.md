# Generador de Exámenes con IA - Gestor de Contenido

Esta aplicación de escritorio para Windows te permite construir una biblioteca de contenido analizado por IA y generar exámenes a partir de ella. El flujo de trabajo se divide en dos fases: **Análisis** y **Generación**.

## Nuevo Flujo de Trabajo

1.  **Fase de Análisis (Inversión Inicial):**
    -   Sube uno o varios documentos (`.pdf`, `.docx`, `.pptx`).
    -   La aplicación los procesa, los divide en fragmentos y utiliza la IA (GPT-4o mini) para extraer y consolidar los conceptos clave en un resumen inteligente.
    -   Este resumen se guarda en tu **"Biblioteca de Contenido"** local con un nombre que tú elijas. Este es el paso más largo y que consume créditos de la API.

2.  **Fase de Generación (Rápido y Reutilizable):**
    -   Selecciona uno o más bloques de contenido de tu biblioteca.
    -   Configura el número de preguntas y los parámetros de la IA.
    -   La aplicación genera un examen **casi instantáneamente** utilizando el contenido ya analizado, sin necesidad de procesar los archivos originales de nuevo.

## Características

-   **Biblioteca de Contenido Persistente:** Todo tu material analizado se guarda localmente para su uso futuro.
-   **Generación Rápida de Exámenes:** Crea exámenes en segundos a partir de contenido pre-procesado.
-   **Eficiencia de Costos:** Analiza un documento una vez y genera infinitos exámenes a partir de él.
-   **Manejo de Archivos Grandes:** La estrategia de "chunking" permite procesar documentos de cualquier tamaño.
-   **Conversión Automática de Imágenes:** Las imágenes en formatos no compatibles son convertidas a PNG.
-   **Manejo Robusto de Errores:** Notificaciones claras para problemas de API, archivos corruptos o demasiado grandes.
-   **Banco de Preguntas:** Un completo administrador para guardar, ver y eliminar preguntas y categorías personalizadas.
-   **Exportación a PDF:** Descarga los resultados del examen en formato PDF, con justificaciones que incluyen citas textuales y un formato claro.
-   **Interfaz de Usuario Profesional:** Diseño moderno con una paleta de grises claros y oscuros.

## Requisitos Previos

1.  **Python 3.8+**.
2.  Una **clave de API de OpenAI** con acceso al modelo `gpt-4o-mini`.
3.  **(Recomendado)** La herramienta `make`. En Windows, puedes obtenerla fácilmente instalando [Git for Windows](https://git-scm.com/download/win) (y usando la terminal Git Bash) o a través de [Chocolatey](https://chocolatey.org/) (`choco install make`).
4.  **Fuentes Unicode para PDF:** Para una correcta visualización de caracteres especiales y acentos en los PDF generados, asegúrate de tener los archivos `DejaVuSansCondensed.ttf` y `DejaVuSansCondensed-Bold.ttf` dentro de la carpeta `assets/fonts/` del proyecto. Puedes descargarlos de [DejaVu Fonts](https://dejavu-fonts.github.io/).

## Instalación y Ejecución

Se recomienda encarecidamente usar el `Makefile` proporcionado, ya que automatiza todo el proceso.

### Método Recomendado (Usando `make`)

1.  **Clona o descarga este repositorio.**

2.  **Abre una terminal** (como Git Bash) en la raíz del proyecto.

3.  **Crea el entorno virtual e instala las dependencias con un solo comando:**
    ```bash
    make install
    ```

4.  **Ejecuta la aplicación:**
    ```bash
    make run
    ```

5.  **Para limpiar el proyecto** (eliminar el entorno virtual y archivos generados):
    ```bash
    make clean
    ```

### Método Manual (Sin `make`)

1.  **Clona o descarga este repositorio.**

2.  **Abre una terminal** en la raíz del proyecto.

3.  **Crea un entorno virtual:**
    ```bash
    python -m venv venv
    ```

4.  **Activa el entorno virtual:**
    ```bash
    .\venv\Scripts\activate
    ```

5.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Ejecuta la aplicación:**
    ```bash
    python app.py
    ```

## Cómo Usar la Aplicación

La interfaz de usuario principal se divide en dos paneles:

1.  **Panel Izquierdo (Biblioteca de Contenido):**
    -   Aquí verás una lista de todo el contenido que has analizado y guardado.
    -   Selecciona un elemento de esta lista para habilitar la generación de exámenes en el panel derecho.
    -   Puedes eliminar contenido que ya no necesites.

2.  **Panel Derecho (Acciones):**
    -   **1. Analizar Nuevos Documentos:**
        -   Usa "Añadir Archivos" para seleccionar tus documentos.
        -   Haz clic en "Analizar y Guardar en Biblioteca". Se te pedirá un nombre para el contenido analizado.
    -   **2. Generar un Examen:**
        -   Primero, selecciona un bloque de contenido de la biblioteca en el panel izquierdo.
        -   Configura el número de preguntas y los parámetros de la IA.
        -   Haz clic en "Generar Examen" para iniciar el proceso.
    -   **Administrar Banco de Preguntas:** Este botón abre una ventana dedicada para organizar y eliminar preguntas guardadas individualmente.

## Empaquetado para Windows (.exe)

Para crear un archivo ejecutable (`.exe`) independiente que no requiera que el usuario tenga Python instalado:

1.  **Instala PyInstaller** en tu entorno virtual:
    ```bash
    pip install pyinstaller
    ```

2.  **Ejecuta el comando de empaquetado** desde la raíz del proyecto:
    ```bash
    pyinstaller --onefile --windowed --name "ExamGenerator" app.py
    ```

3.  El archivo `ExamGenerator.exe` se encontrará en la carpeta `dist`.

## Tecnologías Utilizadas

-   **Python 3**
-   **PyQt6**: para la interfaz gráfica de escritorio.
-   **OpenAI API**: para la generación de contenido con GPT-4o mini.
-   **PyMuPDF (fitz)**: para la extracción de texto e imágenes de archivos PDF.
-   **python-docx**: para procesar documentos de Word.
-   **python-pptx**: para procesar presentaciones de PowerPoint.
-   **Pillow**: para la conversión de imágenes a formatos compatibles.
-   **fpdf2**: para la generación de informes de resultados en PDF.