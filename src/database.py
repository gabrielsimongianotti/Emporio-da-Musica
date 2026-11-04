"""Carregamento dos dados tabulares (CSVs) em SQLite."""

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import (
    CATEGORIES_CSV,
    CUSTOMERS_CSV,
    DATABASE_PATH,
    ORDER_ITEMS_CSV,
    ORDERS_CSV,
    PRODUCTS_CSV,
    PROMOTIONS_CSV,
    logger,
)


def _csv_to_sqlite(csv_path: Path, table_name: str, conn: sqlite3.Connection) -> None:
    """Lê um CSV e insere em uma tabela SQLite."""
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, conn, if_exists="replace", index=False)


def init_database(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Cria o banco SQLite e carrega todos os CSVs."""
    logger.info("Inicializando banco de dados em %s", db_path)

    # Remove banco antigo para garantir dados atualizados
    if db_path.exists():
        db_path.unlink()
        logger.info("Banco antigo removido")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # permite acesso por nome de coluna

    _csv_to_sqlite(CATEGORIES_CSV, "categories", conn)
    _csv_to_sqlite(CUSTOMERS_CSV, "customers", conn)
    _csv_to_sqlite(ORDER_ITEMS_CSV, "order_items", conn)
    _csv_to_sqlite(ORDERS_CSV, "orders", conn)
    _csv_to_sqlite(PRODUCTS_CSV, "products", conn)
    _csv_to_sqlite(PROMOTIONS_CSV, "promotions", conn)

    # Cria índices úteis para consultas
    conn.execute("CREATE INDEX idx_products_category ON products(category_id)")
    conn.execute("CREATE INDEX idx_products_name ON products(name)")
    conn.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
    conn.execute("CREATE INDEX idx_order_items_order ON order_items(order_id)")
    conn.execute("CREATE INDEX idx_promotions_product ON promotions(product_id)")

    conn.commit()
    logger.info("Banco de dados criado com sucesso")
    return conn


def get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Retorna conexão com o banco. Cria o banco se não existir."""
    if not db_path.exists():
        return init_database(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(query: str, params: tuple = ()) -> list[dict]:
    """Executa uma query SQL e retorna os resultados como lista de dicionários."""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
