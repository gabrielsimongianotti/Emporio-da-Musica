.PHONY: setup run test clean help

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup   - Cria venv e instala dependências"
	@echo "  make run     - Executa o agente"
	@echo "  make test    - Roda os testes automatizados"
	@echo "  make clean   - Remove arquivos gerados"

setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	cp .env.example .env
	@echo ""
	@echo "Configuração criada. Edite o arquivo .env e adicione sua OPENAI_API_KEY."

run:
	./venv/bin/python -m src.cli

test:
	./venv/bin/python -m unittest test_tools -v

clean:
	rm -rf venv vector_store emporio_music.db src/__pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
