"""Interface de linha de comando (CLI) do agente Empório da Música."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from src.agent import ask_agent, build_agent
from src.config import OPENAI_API_KEY
from src.database import init_database


def check_api_key(console: Console) -> bool:
    """Verifica se a chave da OpenAI está configurada."""
    if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
        console.print(
            "[bold red]❌ OPENAI_API_KEY não configurada![/bold red]\n"
            "Crie um arquivo .env na raiz do projeto com:\n\n"
            "OPENAI_API_KEY=sk-sua-chave-aqui\n\n"
            "Você pode obter uma chave em: https://platform.openai.com/api-keys"
        )
        return False
    return True


def print_welcome(console: Console) -> None:
    """Exibe mensagem de boas-vindas."""
    welcome_text = Text()
    welcome_text.append("🎸 Bem-vindo à Empório da Música!\n\n", style="bold green")
    welcome_text.append("Sou o assistente virtual da loja e estou aqui para te ajudar.\n")
    welcome_text.append("Pergunte sobre produtos, preços, pedidos, políticas da loja e muito mais.\n\n")
    welcome_text.append("Comandos disponíveis:\n", style="bold")
    welcome_text.append("  /sair   - Encerrar a conversa\n")
    welcome_text.append("  /limpar - Limpar o histórico da conversa")

    console.print(Panel(welcome_text, title="Assistente Virtual", border_style="blue"))


def main() -> None:
    """Ponto de entrada do CLI."""
    console = Console()

    console.print("[yellow]🔄 Inicializando banco de dados...[/yellow]")

    # Inicializa dados tabulares
    init_database()

    console.print("[green]✅ Banco de dados pronto![/green]\n")

    if not check_api_key(console):
        return

    print_welcome(console)

    agent = build_agent()

    while True:
        try:
            user_input = console.input("\n[bold cyan]Você:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold red]Encerrando...[/bold red]")
            break

        if not user_input:
            continue

        if user_input.lower() == "/sair":
            console.print("\n[bold green]🎶 Obrigado por falar com a Empório da Música! Até a próxima![/bold green]")
            break

        if user_input.lower() == "/limpar":
            agent = build_agent()
            console.print("[yellow]🧹 Histórico da conversa limpo.[/yellow]")
            continue

        with console.status("[bold yellow]O assistente está digitando...[/bold yellow]"):
            response = ask_agent(agent, user_input)

        console.print(f"\n[bold green]Empório da Música:[/bold green] {response}\n")


if __name__ == "__main__":
    main()
