"""Configurações centralizadas do projeto."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Diretórios base
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "src"

# Arquivos de dados
CATEGORIES_CSV = DATA_DIR / "desafio_tecnico_ai_eng - categories.csv"
CUSTOMERS_CSV = DATA_DIR / "desafio_tecnico_ai_eng - customers.csv"
ORDER_ITEMS_CSV = DATA_DIR / "desafio_tecnico_ai_eng - order_items.csv"
ORDERS_CSV = DATA_DIR / "desafio_tecnico_ai_eng - orders.csv"
PRODUCTS_CSV = DATA_DIR / "desafio_tecnico_ai_eng - products.csv"
PROMOTIONS_CSV = DATA_DIR / "desafio_tecnico_ai_eng - promotions.csv"
POLICIES_PDF = DATA_DIR / "políticas_da_loja.pdf"

# Banco de dados SQLite
DATABASE_PATH = ROOT_DIR / "emporio_music.db"

# Vector store FAISS
VECTOR_STORE_DIR = ROOT_DIR / "vector_store"

# Configurações do LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))

# Configurações de embeddings
EMBEDDING_MODEL = "text-embedding-3-small"

# Configurações de chunking do PDF
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def validate_config() -> list[str]:
    """Valida as configurações obrigatórias e retorna lista de erros."""
    errors: list[str] = []

    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY não está configurada.")
    elif not OPENAI_API_KEY.startswith("sk-"):
        errors.append("OPENAI_API_KEY parece inválida (deve começar com 'sk-').")

    required_files = [
        ("categories.csv", CATEGORIES_CSV),
        ("customers.csv", CUSTOMERS_CSV),
        ("order_items.csv", ORDER_ITEMS_CSV),
        ("orders.csv", ORDERS_CSV),
        ("products.csv", PRODUCTS_CSV),
        ("promotions.csv", PROMOTIONS_CSV),
        ("políticas_da_loja.pdf", POLICIES_PDF),
    ]

    for name, path in required_files:
        if not path.exists():
            errors.append(f"Arquivo de dados não encontrado: {name} ({path})")

    return errors


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configura o logger do projeto."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("emporio_musica")


logger = setup_logging()
