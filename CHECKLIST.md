# ✅ Checklist de Testes - Agente Empório da Música

Use este arquivo para testar todas as funcionalidades do projeto antes de entregar.

---

## 1. Configuração do ambiente

- [ ] Clonou/copiou o projeto para a máquina
- [ ] Criou o ambiente virtual (`python3 -m venv venv`)
- [ ] Ativou o ambiente virtual (`source venv/bin/activate`)
- [ ] Instalou as dependências (`pip install -r requirements.txt`)
- [ ] Criou o arquivo `.env` a partir do `.env.example`
- [ ] Adicionou uma chave `OPENAI_API_KEY` válida com créditos no `.env`

**Comando para testar:**
```bash
python3 -m src.cli
```

---

## 2. Testes das ferramentas (sem API)

Rode:
```bash
python3 -m unittest test_tools -v
```

- [ ] `test_search_products_with_stock_filter` passou
- [ ] `test_get_product_price_takamine_gd20` passou
- [ ] `test_get_order_status_existing_order` passou
- [ ] `test_get_order_status_non_existing_order` passou
- [ ] `test_get_store_info_contains_address` passou

---

## 3. Cenários de conversa com o agente

Inicie o agente:
```bash
python3 -m src.cli
```

### 3.1 Saudação inicial
- [ ] O agente cumprimenta no tom da Empório da Música
- [ ] Pergunta como pode ajudar

### 3.2 Consulta de catálogo com filtro
**Pergunte:** `Quais opções de violões disponíveis custando até R$1000?`

- [ ] Lista apenas violões
- [ ] Todos os preços são ≤ R$ 1000
- [ ] Mostra estoque
- [ ] Sugere algo ou pergunta se quer mais detalhes

### 3.3 Consulta de preço específico
**Pergunte:** `Quanto custa o Takamine GD20?`

- [ ] Responde o preço correto: R$ 2.199,00
- [ ] Informa que tem estoque (5 unidades)
- [ ] Não inventa informações

### 3.4 Informações gerais da loja
**Pergunte:** `Qual o endereço da loja?`

- [ ] Informa o endereço correto: Rua 14 de Maio, 3200 — Centro, Campo Grande/MS
- [ ] Informa o telefone/WhatsApp
- [ ] Informa o horário de funcionamento

### 3.5 Status de pedido
**Pergunte:** `Qual o status do pedido 8?`

- [ ] Retorna status: enviado (shipped)
- [ ] Retorna código de rastreamento: BRJL5544332BR
- [ ] Retorna nome do cliente: Ana Carolina Ferreira
- [ ] Retorna itens do pedido

### 3.6 Política de devolução (cenário não trivial)
**Pergunte:** `Me arrependi da minha compra, posso devolver meu pedido?`

- [ ] Consulta as políticas da loja
- [ ] Menciona o prazo de 7 dias corridos
- [ ] Menciona embalagem original e sem sinais de uso
- [ ] Menciona reembolso na mesma forma de pagamento
- [ ] Pergunta o número do pedido

**Continuação:** informe `Meu pedido é o 8`

- [ ] Consulta o status do pedido
- [ ] Explica que o prazo conta a partir do recebimento

### 3.7 Pergunta fora de escopo
**Pergunte:** `Vocês vendem cordas de violão?`

- [ ] Explica que a loja vende apenas instrumentos musicais
- [ ] Não confirma venda de acessórios
- [ ] Redireciona educadamente para instrumentos

### 3.8 Memória de conversa
**Pergunte:**
1. `Meu nome é João`
2. `Qual o meu nome?`

- [ ] O agente lembra o nome mencionado anteriormente

### 3.9 Comandos do CLI
- [ ] `/limpar` limpa o histórico da conversa
- [ ] `/sair` encerra a conversa

---

## 4. Casos de borda

### 4.1 Produto fora de estoque
**Pergunte:** `Vocês têm o Giannini GF-3D Dreadnought Sunburst?`

- [ ] Informa que está fora de estoque
- [ ] Sugere alternativas similares

### 4.2 Produto inexistente
**Pergunte:** `Quanto custa o Fender Stratocaster XYZ?`

- [ ] Informa que não encontrou o produto
- [ ] Não inventa preço

### 4.3 Pedido inexistente
**Pergunte:** `Qual o status do pedido 999?`

- [ ] Informa que não encontrou o pedido

### 4.4 Pergunta sobre frete
**Pergunte:** `Quanto custa o frete para São Paulo?`

- [ ] Consulta as políticas de frete
- [ ] Explica as regras gerais (Correios/Jadlog)
- [ ] Não inventa valor específico sem CEP

### 4.5 Pergunta sobre formas de pagamento
**Pergunte:** `Quais formas de pagamento vocês aceitam?`

- [ ] Lista PIX, cartão de débito, cartão de crédito e boleto
- [ ] Menciona desconto de 5% no PIX

---

## 5. Verificação de qualidade

- [ ] Respostas estão em português
- [ ] Tom de voz é informal mas profissional
- [ ] O agente não inventa preços, estoque ou prazos
- [ ] O agente consulta dados antes de responder sobre produtos/pedidos
- [ ] O agente consulta políticas antes de responder sobre trocas/devoluções/frete
- [ ] O agente lida bem com perguntas fora do escopo

---

## 6. Documentação e entrega

- [ ] README.md está completo e claro
- [ ] `.env.example` está configurado
- [ ] `requirements.txt` está atualizado
- [ ] Exemplos de conversa estão na pasta `examples/`
- [ ] Código está no repositório público do GitHub
- [ ] `.env` NÃO foi commitado (está no `.gitignore`)

---

## Comandos úteis

```bash
# Rodar testes automatizados
python3 -m unittest test_tools -v

# Rodar o agente
python3 -m src.cli

# Verificar se .env não está commitado
git status
```

---

*Marque cada item conforme for testando. Se algum falhar, revise o código ou o prompt do agente.*
