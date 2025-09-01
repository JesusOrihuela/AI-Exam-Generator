# Makefile para la aplicacion Generador de Examenes con IA

# --- Version requerida ---
PY_VERSION = 3.8.10

# --- Variables de Configuracion ---

# Intérprete del sistema que se usará para crear el entorno virtual
# (debe apuntar a Python 3.8.10 exactamente)
ifeq ($(OS),Windows_NT)
    # En Windows se usa el Python Launcher. Debe existir 3.8.10 instalado.
    SYSTEM_PYTHON = py -3.8
    PYTHON = $(VENV_DIR)\Scripts\python
    PIP = $(VENV_DIR)\Scripts\pip
    RM_RF_CMD = rmdir /s /q
    RM_FILE_CMD = del
else
    # En Unix/macOS se asume python3.8 en PATH (3.8.10 exacto)
    SYSTEM_PYTHON = python3.8
    PYTHON = $(VENV_DIR)/bin/python
    PIP = $(VENV_DIR)/bin/pip
    RM_RF_CMD = rm -rf
    RM_FILE_CMD = rm
endif

# Nombre del directorio del entorno virtual
VENV_DIR = venv

# Archivo de dependencias
REQUIREMENTS = requirements.txt

# --- Reglas de PHONY ---
.PHONY: help install run clean check-python

# --- Regla por Defecto ---
default: help

# --- Reglas Principales ---

help:
	@echo "--------------------------------------------------------"
	@echo " Makefile para la aplicacion Generador de Examenes con IA"
	@echo "--------------------------------------------------------"
	@echo "Usando Python requerido: $(PY_VERSION)"
	@echo "Comandos disponibles:"
	@echo "  make install    -> Verifica Python $(PY_VERSION), crea venv e instala dependencias."
	@echo "  make run        -> Ejecuta la aplicacion de escritorio (sin __pycache__)."
	@echo "  make clean      -> Elimina el entorno virtual y archivos generados."
	@echo "  make help       -> Muestra este mensaje de ayuda."
	@echo "--------------------------------------------------------"

install: $(VENV_DIR)/pyvenv.cfg
	@echo "Entorno virtual creado con Python $(PY_VERSION) e instalaciones completadas."

run: install
	@echo "Iniciando la aplicacion..."
	@$(PYTHON) -B app.py

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

# --- Verificación estricta de versión de Python ---
check-python:
ifeq ($(OS),Windows_NT)
	@for /f %%V in ('$(SYSTEM_PYTHON) -c "import platform; print(platform.python_version())"') do @if not "%%V"=="$(PY_VERSION)" (echo [ERROR] Se requiere Python $(PY_VERSION) pero se encontro %%V. && exit /b 1) else (echo Python %%V OK.)
else
	@ver_str=`$(SYSTEM_PYTHON) -c 'import platform; print(platform.python_version())'` || { echo "[ERROR] No se encontro interprete para Python $(PY_VERSION)."; exit 1; }; \
	if [ "$$ver_str" != "$(PY_VERSION)" ]; then \
		echo "[ERROR] Se requiere Python $(PY_VERSION), encontrado $$ver_str. Ajusta tu PATH o instala esa version (pyenv recomendado)."; \
		exit 1; \
	else \
		echo "Python $$ver_str OK."; \
	fi
endif

# --- Creación del entorno virtual e instalación de deps ---
$(VENV_DIR)/pyvenv.cfg: $(REQUIREMENTS)
	@$(MAKE) check-python
	@echo "Creando entorno virtual en '$(VENV_DIR)' usando '$(SYSTEM_PYTHON)'..."
	$(SYSTEM_PYTHON) -m venv $(VENV_DIR)
	@echo "Instalando dependencias desde '$(REQUIREMENTS)'..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install -r $(REQUIREMENTS)
