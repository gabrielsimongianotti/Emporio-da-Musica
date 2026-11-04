"""Testes automatizados para as ferramentas do agente.

Roda com:
    python3 -m unittest test_tools -v
"""

import json
import unittest

from src.database import init_database
from src.tools import (
    get_active_promotions,
    get_order_status,
    get_product_price,
    get_store_info,
    search_products,
)


class TestAgentTools(unittest.TestCase):
    """Testa as ferramentas que não dependem de API externa."""

    @classmethod
    def setUpClass(cls) -> None:
        """Recria o banco de dados antes de rodar os testes."""
        init_database()

    def test_search_products_with_stock_filter(self) -> None:
        """Busca violões até R$ 1000 com estoque."""
        result = search_products.invoke(
            {"category": "Violões", "max_price": 1000.0, "in_stock": True}
        )
        data = json.loads(result)

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        # Todos os produtos devem ser da categoria Violões, ter estoque > 0 e preço <= 1000
        for item in data:
            self.assertEqual(item["category"], "Violões")
            self.assertGreater(item["stock_quantity"], 0)
            self.assertLessEqual(item["price_brl"], 1000.0)

    def test_search_products_does_not_return_ukuleles_for_violao(self) -> None:
        """Garante que busca por categoria Violões não retorna ukuleles."""
        result = search_products.invoke(
            {"category": "Violões", "max_price": 1000.0, "in_stock": True}
        )
        data = json.loads(result)

        categories = {item["category"] for item in data}
        self.assertNotIn("Ukuleles", categories)

    def test_get_product_price_takamine_gd20(self) -> None:
        """Consulta o preço do Takamine GD20."""
        result = get_product_price.invoke({"product_name": "Takamine GD20"})
        data = json.loads(result)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_name"], "Takamine GD20 Dreadnought Natural")
        self.assertEqual(data[0]["price_brl"], 2199.0)
        self.assertEqual(data[0]["category"], "Violões")

    def test_get_active_promotions(self) -> None:
        """Lista promoções ativas."""
        result = get_active_promotions.invoke({})
        data = json.loads(result)

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        for item in data:
            self.assertGreater(item["discount_percent"], 0)
            self.assertIn("price_formatted", item)
            self.assertIn("final_price_formatted", item)

    def test_get_order_status_existing_order(self) -> None:
        """Consulta o pedido #8."""
        result = get_order_status.invoke({"order_id": 8})
        data = json.loads(result)

        self.assertEqual(data["order_id"], 8)
        self.assertEqual(data["status"], "shipped")
        self.assertEqual(data["status_label"], "enviado")
        self.assertEqual(data["tracking_code"], "BRJL5544332BR")
        self.assertEqual(data["customer_name"], "Ana Carolina Ferreira")
        self.assertEqual(len(data["items"]), 1)

    def test_get_order_status_non_existing_order(self) -> None:
        """Consulta um pedido inexistente."""
        result = get_order_status.invoke({"order_id": 999})
        self.assertIn("Não encontrei", result)

    def test_get_store_info_contains_address(self) -> None:
        """Verifica se as informações da loja incluem o endereço."""
        result = get_store_info.invoke({})
        self.assertIn("Rua 14 de Maio", result)
        self.assertIn("Campo Grande", result)
        self.assertIn("(67) 3341-4444", result)


if __name__ == "__main__":
    unittest.main()
