"""Configurações centralizadas do projeto."""

import os
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
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Configurações de chunking do PDF
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
