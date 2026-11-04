"""Ferramentas (tools) disponíveis para o agente de atendimento."""

import json
from typing import Optional

from langchain.tools import tool

from src.database import execute_query
from src.embeddings import search_policies


@tool
def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
) -> str:
    """Busca produtos no catálogo por nome, categoria, preço máximo e disponibilidade.

    Args:
        query: Termo de busca no nome ou descrição do produto (ex: "violão", "Takamine").
        category: Nome da categoria (ex: "Violões", "Guitarras").
        max_price: Preço máximo em reais.
        in_stock: Se True, retorna apenas produtos com estoque > 0.

    Returns:
        Lista de produtos encontrados em formato JSON.
    """
    conditions = ["p.status IN ('active', 'coming_soon')"]
    params: list = []

    if query:
        conditions.append("(p.name LIKE ? OR p.description LIKE ?)")
        term = f"%{query}%"
        params.extend([term, term])

    if category:
        conditions.append("c.name LIKE ?")
        params.append(f"%{category}%")

    if max_price is not None:
        conditions.append("p.price_brl <= ?")
        params.append(max_price)

    if in_stock:
        conditions.append("p.stock_quantity > 0")

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            p.name AS product_name,
            p.price_brl,
            p.stock_quantity,
            p.status,
            c.name AS category,
            p.description
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE {where_clause}
        ORDER BY p.price_brl ASC
        LIMIT 10
    """

    rows = execute_query(sql, tuple(params))
    if not rows:
        return "Nenhum produto encontrado com os filtros informados."

    return json.dumps(rows, ensure_ascii=False, indent=2)


@tool
def get_product_price(product_name: str) -> str:
    """Consulta preço e estoque de um produto específico pelo nome.

    Args:
        product_name: Nome ou parte do nome do produto.

    Returns:
        Informações de preço e estoque em formato JSON.
    """
    sql = """
        SELECT
            p.name AS product_name,
            p.price_brl,
            p.stock_quantity,
            p.status,
            c.name AS category
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.name LIKE ?
        LIMIT 5
    """
    rows = execute_query(sql, (f"%{product_name}%",))
    if not rows:
        return f"Não encontrei nenhum produto chamado '{product_name}'."

    return json.dumps(rows, ensure_ascii=False, indent=2)


@tool
def get_order_status(order_id: int) -> str:
    """Consulta status de um pedido pelo número do pedido.

    Args:
        order_id: Número identificador do pedido.

    Returns:
        Informações do pedido em formato JSON.
    """
    sql = """
        SELECT
            o.order_id,
            o.order_date,
            o.status,
            o.total_brl,
            o.payment_method,
            o.tracking_code,
            o.estimated_delivery,
            o.notes,
            c.name AS customer_name
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = ?
    """
    rows = execute_query(sql, (order_id,))
    if not rows:
        return f"Não encontrei nenhum pedido com o número {order_id}."

    order = rows[0]

    # Busca itens do pedido
    items_sql = """
        SELECT p.name AS product_name, oi.quantity, p.price_brl
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        WHERE oi.order_id = ?
    """
    items = execute_query(items_sql, (order_id,))
    order["items"] = items

    return json.dumps(order, ensure_ascii=False, indent=2)


@tool
def get_policies(query: str) -> str:
    """Busca trechos relevantes do manual de políticas da loja.

    Use esta ferramenta para responder sobre trocas, devoluções, garantia,
    frete, formas de pagamento, horário de funcionamento e outras políticas.

    Args:
        query: Pergunta do cliente em português.

    Returns:
        Trechos relevantes do manual de políticas.
    """
    docs = search_policies(query, k=4)
    if not docs:
        return "Não encontrei informações específicas no manual de políticas."

    return "\n\n---\n\n".join(docs)


@tool
def get_store_info() -> str:
    """Retorna informações gerais da loja: endereço, telefone, horário e e-mail.

    Returns:
        Texto com informações da loja.
    """
    return """
Empório da Música
Sua música começa aqui.

Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, 79202-333
Telefone / WhatsApp: (67) 3341-4444
WhatsApp de atendimento: (67) 3321-4500
E-mail: contato@empóriodamusica.com.br
CNPJ: 12.345.678/0001-90

Horário de funcionamento:
- Segunda a Sexta: 09:00 às 18:00
- Sábado: 09:00 às 13:00
- Domingo e Feriados: Fechado
"""


# Lista exposta para fácil importação
TOOLS = [
    search_products,
    get_product_price,
    get_order_status,
    get_policies,
    get_store_info,
]
