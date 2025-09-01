# config.py

# Modelos
MODEL_SUMMARY = "gpt-4.1-mini"
MODEL_EXAM = "gpt-4.1-mini"
MODEL_VISION = "gpt-4.1-mini"
EMBEDDINGS_MODEL = "text-embedding-3-small"

MAX_SUMMARY_CHARS_FOR_GEN = 70000

# Analizador multimodal (bloques)
TOKENS_PER_BLOCK_MIN = 1000
TOKENS_PER_BLOCK_MAX = 1400

# Selección de imágenes (ingesta)
MAX_IMGS_PER_BLOCK = 2
MAX_IMGS_PER_PAGE = 2
IMAGE_TOKEN_EQUIV = 400
MIN_IMAGE_AREA = 40000
DEDUPLICATE_IMAGES = True

# OCR
OCR_ENABLED = True
OCR_MODE = "auto"          # "auto" | "local" | "llm" | "off"
OCR_LANG = "spa+eng"       # idioma(s) para Tesseract si está disponible
OCR_TEXT_MAX_CHARS = 1200
OCR_TOKEN_ESTIMATE = 600

# Segmentación semántica
SEMANTIC_SPLIT_ENABLED = True
SEMANTIC_SIM_THRESHOLD = 0.82
SEMANTIC_MIN_TOKENS = 400
SEMANTIC_TARGET_TOKENS = 1000
SEMANTIC_MAX_SENTENCES = 1800

# Presupuesto por minuto
TPM_BUDGET = 80000
RPM_BUDGET = 60
CONCURRENCY = 1
COOLDOWN_MS = 800
