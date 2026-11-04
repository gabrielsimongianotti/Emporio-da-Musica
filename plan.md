# Plano de Implementação - Agente de Atendimento Empório da Música

## 1. Visão Geral

Construir um agente de atendimento em Python para a **Empório da Música**, loja fictícia de instrumentos musicais em Campo Grande/MS. O agente deve responder dúvidas de clientes consultando dados operacionais (produtos, pedidos, clientes, promoções) e políticas da loja (PDF), sempre no tom informal-profissional definido no manual.

## 2. Decisões Técnicas

### 2.1 LLM e Provedor
- **Provedor:** OpenAI
- **Modelo:** `gpt-4o-mini`
- **Justificativa:** bom custo-benefício, excelente suporte a function calling, respostas rápidas e confiáveis em português.

### 2.2 Framework
- **LangChain** para orquestração de agente, tools e memória.
- **Justificativa:** abstrai o boilerplate de integração com OpenAI, gerencia histórico de conversa e simplifica a criação de ferramentas.

### 2.3 Dados Tabulares
- **SQLite** carregado a partir dos CSVs.
- **Justificativa:** não requer servidor, é nativo do Python, permite consultas SQL precisas para preços, estoque e status de pedido.

### 2.4 Dados Não Estruturados (PDF de Políticas)
- **ChromaDB** como vector store.
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace.
- **Justificativa:** busca semântica simples e eficiente para recuperar trechos relevantes do manual.

### 2.5 Interface
- **CLI (terminal)** usando `rich` para estilização.
- **Justificativa:** simples de implementar, fácil de testar, parece uma conversa de WhatsApp e gera exemplos limpos em `.md`.

### 2.6 Memória
- Histórico da conversa mantido em memória durante a sessão do CLI (via `ConversationBufferMemory` do LangChain).
- **Justificativa:** suficiente para demonstrar contexto de conversa sem adicionar complexidade de banco de histórico.

## 3. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                      USUÁRIO (CLI/Rich)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                         AGENTE (LangChain)                   │
│   - Interpreta intenção                                      │
│   - Escolhe ferramenta (tool)                                │
│   - Mantém histórico de conversa                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Tool: SQL  │  │ Tool: RAG   │  │  Tool: Info │
│  Produtos,  │  │  Políticas  │  │    Gerais   │
│  Pedidos,   │  │   da Loja   │  │             │
│  Clientes   │  │             │  │             │
└──────┬──────┘  └──────┬──────┘  └─────────────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────────────┐
│   SQLite    │  │      ChromaDB       │
│   (dados    │  │   + embeddings      │
│   tabulares)│  │   sentence-transformers │
└─────────────┘  └─────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM (OpenAI gpt-4o-mini)                  │
│              Gera a resposta final em português              │
└─────────────────────────────────────────────────────────────┘
```

## 4. Ferramentas (Tools)

1. **`search_products(query, category, max_price, in_stock)`**
   - Busca produtos no SQLite por nome, categoria, preço máximo e disponibilidade.

2. **`get_product_price(product_name)`**
   - Retorna preço e estoque de um produto específico.

3. **`get_order_status(order_id)`**
   - Consulta status, data e código de rastreamento de um pedido.

4. **`get_policies(query)`**
   - Busca trechos relevantes do PDF de políticas usando ChromaDB.

5. **`get_store_info()`**
   - Retorna informações fixas da loja (endereço, telefone, horário).

## 5. Fluxo de Decisão do Agente

```
Pergunta do cliente
        │
        ▼
┌──────────────────┐
│  Fora de escopo? │──Sim──► "Só trabalhamos com instrumentos musicais..."
└────────┬─────────┘
         │ Não
         ▼
┌──────────────────┐
│  Precisa de      │
│  dados/dados?    │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
Produto   Política
/Pedido   /Loja
    │         │
    ▼         ▼
  SQLite   ChromaDB
    │         │
    └────┬────┘
         ▼
   LLM gera resposta
```

## 6. Estrutura de Arquivos

```
.
├── .env.example
├── .gitignore
├── plan.md
├── README.md
├── requirements.txt
├── examples/
│   ├── exemplo_01_catalogo.md
│   ├── exemplo_02_endereco.md
│   ├── exemplo_03_preco.md
│   ├── exemplo_04_devolucao.md
│   └── exemplo_05_fora_escopo.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── embeddings.py
│   ├── tools.py
│   ├── agent.py
│   └── cli.py
└── data/
    ├── *.csv
    └── políticas_da_loja.pdf
```

## 7. Etapas de Implementação

1. Criar estrutura base do projeto (`requirements.txt`, `.env.example`, `.gitignore`).
2. Criar módulo `database.py` para carregar CSVs no SQLite.
3. Criar módulo `embeddings.py` para carregar PDF no ChromaDB.
4. Criar módulo `tools.py` com as ferramentas do agente.
5. Criar módulo `agent.py` com o agente LangChain, prompt de sistema e memória.
6. Criar módulo `cli.py` com interface de terminal usando `rich`.
7. Criar exemplos de conversa em `examples/`.
8. Escrever README.md com instruções de execução e justificativas.
9. Testar o agente e corrigir problemas.

## 8. Limitações Conhecidas (a documentar no README)

- O histórico de conversa não persiste entre sessões do CLI.
- O agente não realiza pedidos nem processa pagamentos.
- Números de pedido precisam ser informados pelo cliente; não há identificação por telefone nesta versão.
- Promoções são consultadas por produto; não há cálculo automático de frete por CEP.

## 9. Exemplos de Interação a Gerar

1. **Catálogo com filtro:** "Quais opções de violões disponíveis custando até R$1000?"
2. **Informações gerais:** "Qual o endereço da loja?"
3. **Preço específico:** "Quanto custa o Takamine GD20?"
4. **Política não trivial:** "Me arrependi da minha compra, posso devolver meu pedido?"
5. **Fora de escopo:** "Vocês vendem cordas de violão?"

---

*Plano criado durante a fase de planejamento do desafio técnico.*
