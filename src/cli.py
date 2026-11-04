"""Interface de linha de comando (CLI) do agente Empório da Música."""

import warnings

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from src.agent import ask_agent, build_agent
from src.config import OPENAI_API_KEY
from src.database import init_database

# Suprime deprecation warnings do LangChain para não poluir a interface
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def check_api_key(console: Console) -> bool:
    """Verifica se a chave da OpenAI está configurada."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        console.print(
            "[bold red]OPENAI_API_KEY não configurada![/bold red]\n"
            "Crie um arquivo .env na raiz do projeto com:\n\n"
            "OPENAI_API_KEY=sk-sua-chave-aqui\n\n"
            "Você pode obter uma chave em: https://platform.openai.com/api-keys"
        )
        return False
    return True


def print_welcome(console: Console) -> None:
    """Exibe mensagem de boas-vindas."""
    welcome_text = Text()
    welcome_text.append("Bem-vindo à Empório da Música!\n\n", style="bold green")
    welcome_text.append("Sou o assistente virtual da loja e estou aqui para te ajudar.\n")
    welcome_text.append("Pergunte sobre produtos, preços, pedidos, políticas da loja e muito mais.\n\n")
    welcome_text.append("Comandos disponíveis:\n", style="bold")
    welcome_text.append("  /sair   - Encerrar a conversa\n")
    welcome_text.append("  /limpar - Limpar o histórico da conversa\n")
    welcome_text.append("  /ajuda  - Mostrar ajuda")

    console.print(Panel(welcome_text, title="Assistente Virtual", border_style="blue"))


def print_help(console: Console) -> None:
    """Exibe mensagem de ajuda."""
    help_text = """
Comandos disponíveis:
  /sair   - Encerrar a conversa
  /limpar - Limpar o histórico da conversa
  /ajuda  - Mostrar esta ajuda

Exemplos de perguntas:
  Quais violões até R$ 1000?
  Quanto custa o Takamine GD20?
  Qual o status do pedido 8?
  Vocês vendem cordas de violão?
"""
    console.print(Panel(help_text, title="Ajuda", border_style="green"))


def print_agent_response(console: Console, response: str) -> None:
    """Exibe a resposta do agente formatada."""
    # Renderiza Markdown se houver listas/ênfases, mas mantém texto puro
    markdown = Markdown(response)
    console.print(Panel(markdown, title="Empório da Música", border_style="green"))


def main() -> None:
    """Ponto de entrada do CLI."""
    console = Console()

    console.print("[yellow]Inicializando banco de dados...[/yellow]")

    try:
        init_database()
    except Exception as exc:
        console.print(f"[bold red]Erro ao inicializar banco de dados:[/bold red] {exc}")
        return

    console.print("[green]Banco de dados pronto![/green]\n")

    if not check_api_key(console):
        return

    print_welcome(console)

    try:
        agent = build_agent()
    except Exception as exc:
        console.print(f"[bold red]Erro ao inicializar o agente:[/bold red] {exc}")
        return

    while True:
        try:
            user_input = console.input("\n[bold cyan]Você:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold red]Encerrando...[/bold red]")
            break

        if not user_input:
            continue

        command = user_input.lower()

        if command == "/sair":
            console.print("\n[bold green]Obrigado por falar com a Empório da Música! Até a próxima![/bold green]")
            break

        if command == "/limpar":
            try:
                agent = build_agent()
                console.print("[yellow]Histórico da conversa limpo.[/yellow]")
            except Exception as exc:
                console.print(f"[bold red]Erro ao limpar histórico:[/bold red] {exc}")
            continue

        if command == "/ajuda":
            print_help(console)
            continue

        with console.status("[bold yellow]O assistente está digitando...[/bold yellow]"):
            try:
                response = ask_agent(agent, user_input)
            except Exception as exc:
                console.print(
                    f"\n[bold red]Ops! Algo deu errado:[/bold red] {exc}\n"
                    "Tente novamente ou verifique sua chave da OpenAI."
                )
                continue

        print_agent_response(console, response)


if __name__ == "__main__":
    main()
