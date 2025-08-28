# Makefile para la aplicacion Generador de Examenes con IA

# --- Variables de Configuracion ---

# ESPECIFICA AQUI LA VERSION DE PYTHON A USAR PARA CREAR EL ENTORNO VIRTUAL.
# Asegurate de que esta version de Python este instalada y disponible en tu PATH.
# Ejemplos: python3.10, python3.11, python3.12, o simplemente 'python' para la version por defecto.
SYSTEM_PYTHON = python

# Nombre del directorio del entorno virtual
VENV_DIR = venv

# Deteccion del sistema operativo para usar el interprete de Python correcto
ifeq ($(OS),Windows_NT)
    PYTHON = $(VENV_DIR)\Scripts\python
    PIP = $(VENV_DIR)\Scripts\pip
    RM_RF_CMD = rmdir /s /q
    RM_FILE_CMD = del
else
    PYTHON = $(VENV_DIR)/bin/python
    PIP = $(VENV_DIR)/bin/pip
    RM_RF_CMD = rm -rf
    RM_FILE_CMD = rm
endif

# Archivo de dependencias
REQUIREMENTS = requirements.txt

# --- Reglas dePHONY ---
.PHONY: help install run clean

# --- Regla por Defecto ---
default: help

# --- Reglas Principales ---

help:
	@echo "--------------------------------------------------------"
	@echo " Makefile para la aplicacion Generador de Examenes con IA          "
	@echo "--------------------------------------------------------"
	@echo "Comandos disponibles:"
	@echo "  make install    -> Crea el entorno virtual e instala las dependencias."
	@echo "  make run        -> Ejecuta la aplicacion de escritorio."
	@echo "  make clean      -> Elimina el entorno virtual y otros archivos generados."
	@echo "  make help       -> Muestra este mensaje de ayuda."
	@echo "--------------------------------------------------------"

install: $(VENV_DIR)/pyvenv.cfg
	@echo "Entorno virtual creado y dependencias instaladas con exito."

run: install
	@echo "Iniciando la aplicacion..."
	@$(PYTHON) app.py

clean:
	@echo "Limpiando el proyecto..."
	@if exist $(VENV_DIR) ($(RM_RF_CMD) $(VENV_DIR))
	@if exist exams ($(RM_RF_CMD) exams)
	@if exist content_library ($(RM_RF_CMD) content_library)
	@if exist dist ($(RM_RF_CMD) dist)
	@if exist build ($(RM_RF_CMD) build)
	@if exist __pycache__ ($(RM_RF_CMD) __pycache__)
	@if exist logic\__pycache__ ($(RM_RF_CMD) logic\__pycache__)
	@if exist ui\__pycache__ ($(RM_RF_CMD) ui\__pycache__)
	@if exist question_bank.json ($(RM_FILE_CMD) question_bank.json)
	@if exist reported_questions.jsonl ($(RM_FILE_CMD) reported_questions.jsonl)
	@echo "Limpieza completada."

# --- Reglas de Archivos (Dependencias) ---

# Esta regla crea el entorno virtual.
# Solo se ejecuta si el directorio $(VENV_DIR) no existe.
$(VENV_DIR)/pyvenv.cfg: $(REQUIREMENTS)
	@echo "Creando entorno virtual en '$(VENV_DIR)' usando '$(SYSTEM_PYTHON)'..."
	$(SYSTEM_PYTHON) -m venv $(VENV_DIR)
	@echo "Instalando dependencias desde '$(REQUIREMENTS)'..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)