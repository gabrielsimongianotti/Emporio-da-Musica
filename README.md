# Agente de Atendimento - Empório da Música

Assistente virtual de atendimento ao cliente para a **Empório da Música**, loja fictícia de instrumentos musicais em Campo Grande/MS.

O agente responde dúvidas sobre produtos, preços, estoque, status de pedidos, políticas da loja e promoções, consultando dados operacionais e o manual interno de atendimento.

---

## Funcionalidades

- Consulta de catálogo: busca produtos por nome, categoria, faixa de preço e disponibilidade
- Consulta de preços: retorna preço original, preço com desconto e estoque
- Promoções ativas: lista produtos em promoção no momento
- Status de pedidos: consulta status, total, forma de pagamento, código de rastreamento e itens
- Políticas da loja: responde sobre trocas, devoluções, garantia, frete, pagamento e horários usando RAG sobre o PDF
- Informações gerais: endereço, telefone, WhatsApp, e-mail e horário de funcionamento
- Memória de conversa: mantém o contexto da conversa atual
- Fora de escopo: educadamente redireciona perguntas sobre acessórios ou assuntos não relacionados

---

## Arquitetura

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
│  Promoções  │  │             │  │             │
└──────┬──────┘  └──────┬──────┘  └─────────────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌─────────────────────┐
│   SQLite    │  │       FAISS         │
│   (dados    │  │   + OpenAI Embeddings   │
│   tabulares)│  │                     │
└─────────────┘  └─────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM (OpenAI gpt-4o-mini)                  │
│              Gera a resposta final em português              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tecnologias

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Linguagem | Python 3.10+ | Exigência do desafio |
| Framework de agente | LangChain | Orquestração de LLM, tools e memória |
| LLM | OpenAI `gpt-4o-mini` | Custo-benefício e excelente function calling |
| Embeddings | OpenAI `text-embedding-3-small` | Qualidade, baixo custo e simplicidade |
| Vector store | FAISS-CPU | Leve e eficiente para busca semântica |
| Banco de dados | SQLite | Nativo do Python, sem servidor |
| Interface | CLI com `rich` | Simples, rápida e parece uma conversa de WhatsApp |
| Variáveis de ambiente | `python-dotenv` | Segurança da chave de API |

---

## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/emporio-musica-agent.git
cd emporio-musica-agent
```

### 2. Configure o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure a chave da OpenAI

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da OpenAI:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
```

Você pode criar uma chave em: https://platform.openai.com/api-keys

### 5. Execute o agente

```bash
python -m src.cli
```

A primeira execução pode demorar alguns segundos, pois o agente:
- Carrega os CSVs para o SQLite
- Lê o PDF de políticas
- Gera os embeddings e cria o índice FAISS

### Comandos do CLI

| Comando | Ação |
|---------|------|
| `/sair` | Encerra a conversa |
| `/limpar` | Limpa o histórico da conversa |
| `/ajuda` | Mostra ajuda |

---

## Estrutura do projeto

```
.
├── .env.example
├── .gitignore
├── CHECKLIST.md           # checklist de testes manuais
├── plan.md
├── README.md
├── requirements.txt
├── test_tools.py          # testes automatizados das ferramentas
├── data/                  # dados fornecidos pelo desafio
│   ├── *.csv
│   └── políticas_da_loja.pdf
├── examples/              # exemplos de conversa
│   ├── exemplo_01_catalogo.md
│   ├── exemplo_02_endereco.md
│   ├── exemplo_03_preco.md
│   ├── exemplo_04_devolucao.md
│   ├── exemplo_05_fora_escopo.md
│   └── exemplo_06_promocoes.md
└── src/
    ├── __init__.py
    ├── agent.py           # configuração do agente LangChain
    ├── cli.py             # interface de linha de comando
    ├── config.py          # caminhos, variáveis de ambiente e logging
    ├── database.py        # carga dos CSVs no SQLite
    ├── embeddings.py      # carga do PDF no FAISS
    └── tools.py           # ferramentas do agente
```

---

## Decisões técnicas

### Por que LangChain?
LangChain abstrai a complexidade de conectar LLMs, ferramentas e memória. Permite criar um agente que decide sozinho quando consultar dados, quando buscar políticas e quando responder diretamente.

### Por que SQLite?
Os dados são tabulares e pequenos. SQLite é nativo do Python, não precisa de servidor e responde consultas SQL precisas. Isso é essencial para não inventar preços ou estoque.

### Por que RAG com FAISS?
O manual de políticas é um documento não estruturado. Com RAG, dividimos o PDF em trechos, geramos embeddings e buscamos semanticamente os trechos relevantes. Isso evita enviar o PDF inteiro para o LLM e reduz custo e alucinação.

### Por que OpenAI Embeddings?
Embeddings locais (como sentence-transformers) exigem PyTorch/TensorFlow, que aumentam muito o tamanho do projeto. OpenAI Embeddings é leve, rápido, barato e já integrado ao fluxo de API.

### Por que FAISS-CPU em vez de ChromaDB?
FAISS-CPU é mais leve e tem menos dependências. ChromaDB exige pacotes como onnxruntime, que complicam a instalação em ambientes com pouco espaço.

### Por que CLI?
É a interface mais simples de implementar e testar. Parece uma conversa de WhatsApp, o que facilita gerar os exemplos de interação exigidos pelo desafio.

### Estratégia de prompt
O prompt de sistema define:
- Persona do atendente (informal mas profissional)
- Dados fixos da loja
- Fluxo de atendimento em 5 passos
- Quando usar cada ferramenta
- Regras de escopo (apenas instrumentos musicais)
- Proibição de inventar preços, prazos ou políticas
- Exemplos de bom e mau tom

### Tratamento dos dados
- CSVs são carregados no SQLite com índices para consultas rápidas
- Preços e datas são formatados no padrão brasileiro
- Status de pedidos são traduzidos para português
- Promoções ativas são consultadas junto com produtos e pedidos
- Produtos fora de estoque são identificados corretamente

---

## Limitações conhecidas

- O histórico de conversa não persiste entre sessões do CLI.
- O agente não realiza pedidos, reservas ou processamento de pagamentos.
- Não identifica clientes automaticamente pelo telefone; o número do pedido precisa ser informado.
- O cálculo de frete por CEP específico não está implementado; apenas as regras gerais do manual são consultadas.
- O agente depende de créditos na API da OpenAI para funcionar.

### O que faria com mais tempo
- Persistir histórico de conversas em SQLite.
- Adicionar autenticação do cliente por telefone para consultar pedidos sem informar o número.
- Implementar cálculo de frete consultando uma API de CEP.
- Criar uma interface web com Streamlit ou FastAPI.
- Adicionar testes de integração com o LLM.
- Implementar cache de embeddings para atualizações incrementais do PDF.
- Adicionar fallback para modelos locais (Ollama) quando a OpenAI estiver indisponível.

---

## Uso de assistentes de código

Durante o desenvolvimento deste projeto, utilizei assistentes de IA para:
- Estruturar o plano de implementação
- Escrever os primeiros rascunhos dos módulos Python
- Revisar dependências e sugerir alternativas mais leves
- Criar exemplos de conversa e documentação
- Refinar o prompt de sistema e a arquitetura

Todas as decisões técnicas foram validadas e ajustadas manualmente. O código final foi testado e organizado para ser legível e de fácil manutenção.

---

## Exemplos de interação

Os exemplos de conversa estão na pasta `examples/`:

1. `exemplo_01_catalogo.md` — Consulta ao catálogo com filtro de preço
2. `exemplo_02_endereco.md` — Informações gerais da loja
3. `exemplo_03_preco.md` — Consulta de preço com promoção ativa
4. `exemplo_04_devolucao.md` — Cenário não trivial: devolução + status do pedido
5. `exemplo_05_fora_escopo.md` — Pergunta fora do escopo (acessórios)
6. `exemplo_06_promocoes.md` — Consulta de promoções ativas

---

## Testes

Para rodar os testes automatizados das ferramentas:

```bash
python3 -m unittest test_tools -v
```

Para testar manualmente todas as funcionalidades, siga o `CHECKLIST.md`.

---

## Licença

Este projeto foi desenvolvido como parte de um desafio técnico. Os dados da Empório da Música são fictícios.
