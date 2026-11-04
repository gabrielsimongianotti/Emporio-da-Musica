"""Ferramentas (tools) disponíveis para o agente de atendimento."""

import json
from typing import Optional

from langchain.tools import tool

from src.database import execute_query
from src.embeddings import search_policies


def _format_price(value: float) -> str:
    """Formata um valor numérico para o formato brasileiro de moeda."""
    return f"R$ {value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")


def _format_product_rows(rows: list[dict]) -> list[dict]:
    """Adiciona campo de preço formatado e status legível aos produtos."""
    for row in rows:
        row["price_formatted"] = _format_price(row["price_brl"])
        row["availability"] = (
            "disponível" if row["stock_quantity"] > 0 else "fora de estoque"
        )
    return rows


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

    if category:
        # Busca exata na categoria, com fallback para correspondência parcial
        conditions.append("(c.name = ? OR c.name LIKE ?)")
        params.extend([category, f"%{category}%"])

    if query:
        # Se categoria foi informada, busca apenas no nome do produto.
        # Caso contrário, busca no nome e na descrição.
        if category:
            conditions.append("p.name LIKE ?")
            params.append(f"%{query}%")
        else:
            conditions.append("(p.name LIKE ? OR p.description LIKE ?)")
            term = f"%{query}%"
            params.extend([term, term])

    if max_price is not None:
        conditions.append("p.price_brl <= ?")
        params.append(max_price)

    if in_stock:
        conditions.append("p.stock_quantity > 0")

    where_clause = " AND ".join(conditions)

    sql = f"""
        SELECT
            p.product_id,
            p.name AS product_name,
            p.price_brl,
            p.price_brl * (1 - COALESCE(MAX(pr.discount_percent), 0) / 100.0) AS final_price_brl,
            p.stock_quantity,
            p.status,
            c.name AS category,
            p.description,
            COALESCE(MAX(pr.discount_percent), 0) AS discount_percent
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        WHERE {where_clause}
        GROUP BY p.product_id
        ORDER BY p.price_brl ASC
        LIMIT 10
    """

    rows = execute_query(sql, tuple(params))
    if not rows:
        return "Nenhum produto encontrado com os filtros informados."

    _format_product_rows(rows)
    for row in rows:
        row["final_price_formatted"] = _format_price(row["final_price_brl"])
        if row["discount_percent"] > 0:
            row["promotion"] = f"{int(row['discount_percent'])}% de desconto ativo"

    return json.dumps(rows, ensure_ascii=False, indent=2)


@tool
def get_product_price(product_name: str) -> str:
    """Consulta preço, estoque e promoções ativas de um produto específico pelo nome.

    Args:
        product_name: Nome ou parte do nome do produto.

    Returns:
        Informações de preço, estoque e promoções em formato JSON.
    """
    sql = """
        SELECT
            p.product_id,
            p.name AS product_name,
            p.price_brl,
            p.price_brl * (1 - COALESCE(MAX(pr.discount_percent), 0) / 100.0) AS final_price_brl,
            p.stock_quantity,
            p.status,
            c.name AS category,
            COALESCE(MAX(pr.discount_percent), 0) AS discount_percent,
            GROUP_CONCAT(pr.description, ', ') AS active_promotions
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        LEFT JOIN promotions pr ON p.product_id = pr.product_id AND pr.is_active = 1
        WHERE p.name LIKE ?
        GROUP BY p.product_id
        LIMIT 5
    """
    rows = execute_query(sql, (f"%{product_name}%",))
    if not rows:
        return f"Não encontrei nenhum produto chamado '{product_name}'."

    _format_product_rows(rows)
    for row in rows:
        row["price_formatted"] = _format_price(row["price_brl"])
        row["final_price_formatted"] = _format_price(row["final_price_brl"])

    return json.dumps(rows, ensure_ascii=False, indent=2)


@tool
def get_active_promotions() -> str:
    """Lista todas as promoções ativas no momento.

    Returns:
        Lista de promoções ativas em formato JSON.
    """
    sql = """
        SELECT
            p.name AS product_name,
            p.price_brl,
            p.price_brl * (1 - pr.discount_percent / 100.0) AS final_price_brl,
            pr.discount_percent,
            pr.description
        FROM promotions pr
        JOIN products p ON pr.product_id = p.product_id
        WHERE pr.is_active = 1
        ORDER BY pr.discount_percent DESC
    """
    rows = execute_query(sql)
    if not rows:
        return "Não há promoções ativas no momento."

    for row in rows:
        row["price_formatted"] = _format_price(row["price_brl"])
        row["final_price_formatted"] = _format_price(row["final_price_brl"])

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
            c.name AS customer_name,
            c.phone AS customer_phone
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_id = ?
    """
    rows = execute_query(sql, (order_id,))
    if not rows:
        return f"Não encontrei nenhum pedido com o número {order_id}."

    order = rows[0]

    # Traduz status para português
    status_translation = {
        "pending": "pendente",
        "confirmed": "confirmado",
        "shipped": "enviado",
        "delivered": "entregue",
        "cancelled": "cancelado",
    }
    order["status_label"] = status_translation.get(order["status"], order["status"])

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

Atendimento via WhatsApp:
- Mensagens respondidas em até 5 minutos durante o horário de funcionamento.
- Fora do expediente, o assistente informa o horário de retorno.
"""


# Lista exposta para fácil importação
TOOLS = [
    search_products,
    get_product_price,
    get_active_promotions,
    get_order_status,
    get_policies,
    get_store_info,
]
