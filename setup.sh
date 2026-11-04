#!/usr/bin/env bash
# Script de setup do projeto Empório da Música Agent

set -e

echo "=============================================="
echo "  Setup - Agente Empório da Música"
echo "=============================================="
echo ""

# Verifica se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: python3 não encontrado. Instale o Python 3.10 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "Python encontrado: $PYTHON_VERSION"

# Cria ambiente virtual
echo ""
echo "Criando ambiente virtual..."
python3 -m venv venv

# Ativa o ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza o pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instala dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Cria o arquivo .env se não existir
if [ ! -f .env ]; then
    echo ""
    echo "Criando arquivo .env a partir de .env.example..."
    cp .env.example .env
    echo ""
    echo "IMPORTANTE: Edite o arquivo .env e adicione sua OPENAI_API_KEY."
    echo "Você pode obter uma chave em: https://platform.openai.com/api-keys"
else
    echo ""
    echo "Arquivo .env já existe. Verifique se a OPENAI_API_KEY está configurada."
fi

echo ""
echo "=============================================="
echo "  Setup concluído!"
echo "=============================================="
echo ""
echo "Para ativar o ambiente virtual, execute:"
echo "  source venv/bin/activate"
echo ""
echo "Para rodar o agente, execute:"
echo "  python -m src.cli"
echo ""
echo "Para rodar os testes, execute:"
echo "  python -m unittest test_tools -v"
echo ""
