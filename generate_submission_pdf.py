"""Gera o PDF de submissão do case técnico da Artefact."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPO_URL = "https://github.com/gabrielsimongianotti/Emporio-da-Musica"
NAME = "Gabriel Simon Gianotti"
POSITION = "AI Engineer – Full-Stack para Aplicações com IA Generativa"


def create_pdf(output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=20,
        alignment=1,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=30,
        alignment=1,
    )
    heading2_style = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=10,
        spaceBefore=20,
    )
    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=10,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=6,
    )

    story = []

    # Title
    story.append(Paragraph(NAME, title_style))
    story.append(Paragraph(POSITION, subtitle_style))
    story.append(Spacer(1, 0.5 * cm))

    # Repository
    story.append(Paragraph("Project Repository", heading2_style))
    story.append(Paragraph(f'<a href="{REPO_URL}" color="blue">{REPO_URL}</a>', normal_style))
    story.append(Spacer(1, 0.3 * cm))

    # Overview
    story.append(Paragraph("Project Overview", heading2_style))
    story.append(
        Paragraph(
            "This project implements a text-message customer service agent for Empório da Música, "
            "a fictional musical instruments store located in Campo Grande/MS, Brazil. "
            "The agent assists customers by answering questions about products, prices, stock, "
            "order status, store policies, and active promotions.",
            normal_style,
        )
    )

    # Key features
    story.append(Paragraph("Key Features", heading2_style))
    features = [
        "Product catalog search by name, category, price range, and stock availability",
        "Specific product price queries, including active promotions",
        "Active promotions listing",
        "Order status tracking with customer and item details",
        "Policy retrieval using RAG over the store's internal PDF manual",
        "General store information (address, phone, hours)",
        "Out-of-scope handling (redirects accessories requests politely)",
        "Conversation memory within the CLI session",
    ]
    for feature in features:
        story.append(Paragraph(f"• {feature}", bullet_style))

    # Architecture
    story.append(Paragraph("Architecture", heading2_style))
    story.append(
        Paragraph(
            "The solution follows a modular agent architecture built with LangChain and OpenAI:",
            normal_style,
        )
    )
    arch_points = [
        "LLM: OpenAI GPT-4o-mini for natural language understanding and generation",
        "Framework: LangChain for tool orchestration and conversation memory",
        "Structured data: SQLite loaded from CSVs (products, orders, customers, promotions)",
        "Unstructured data: FAISS vector store with OpenAI embeddings for the policy PDF",
        "Interface: CLI with rich formatting, simulating a WhatsApp conversation",
    ]
    for point in arch_points:
        story.append(Paragraph(f"• {point}", bullet_style))

    # Technical decisions
    story.append(Paragraph("Technical Decisions", heading2_style))
    decisions = [
        ("LangChain", "Abstracts LLM integration, tool calling, and memory management, enabling rapid prototyping of a decision-making agent."),
        ("OpenAI GPT-4o-mini", "Offers excellent function calling capabilities and reliable Portuguese responses at a low cost."),
        ("SQLite", "Native to Python, requires no server, and enables precise SQL queries for prices, stock, and order status."),
        ("FAISS + OpenAI Embeddings", "Lightweight semantic search over the policy PDF without adding heavy local dependencies such as PyTorch."),
        ("CLI with rich", "Simple to implement and test; closely resembles a chat interface and makes it easy to generate example conversations."),
    ]
    table_data = [[Paragraph("Decision", heading2_style), Paragraph("Reasoning", heading2_style)]]
    for decision, reasoning in decisions:
        table_data.append([Paragraph(decision, normal_style), Paragraph(reasoning, normal_style)])

    table = Table(table_data, colWidths=[4.5 * cm, 11 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)

    # How to run
    story.append(Paragraph("How to Run", heading2_style))
    story.append(Paragraph("1. Clone the repository and enter the project folder.", normal_style))
    story.append(Paragraph("2. Create a virtual environment: python3 -m venv venv", bullet_style))
    story.append(Paragraph("3. Activate it: source venv/bin/activate", bullet_style))
    story.append(Paragraph("4. Install dependencies: pip install -r requirements.txt", bullet_style))
    story.append(Paragraph("5. Copy .env.example to .env and add your OPENAI_API_KEY.", bullet_style))
    story.append(Paragraph("6. Run the agent: python -m src.cli", bullet_style))

    # Tests
    story.append(Paragraph("Automated Tests", heading2_style))
    story.append(
        Paragraph(
            "The project includes 7 unit tests covering the data tools: product search, price query, "
            "active promotions, order status (existing and non-existing), and store information. "
            "Run them with: python -m unittest test_tools -v",
            normal_style,
        )
    )

    # Examples
    story.append(Paragraph("Conversation Examples", heading2_style))
    story.append(
        Paragraph(
            "Six conversation examples are included in the examples/ folder, covering catalog queries, "
            "store information, specific pricing, return policy (non-trivial scenario), out-of-scope handling, "
            "and active promotions.",
            normal_style,
        )
    )

    # Limitations
    story.append(Paragraph("Known Limitations", heading2_style))
    limitations = [
        "Conversation history does not persist across CLI sessions",
        "The agent does not process orders or payments",
        "Customer identification by phone is not implemented; order number is required",
        "Freight calculation by ZIP code is not implemented; only general rules are provided",
        "Requires OpenAI API credits to function",
    ]
    for limitation in limitations:
        story.append(Paragraph(f"• {limitation}", bullet_style))

    # AI usage
    story.append(Paragraph("Use of AI Coding Assistants", heading2_style))
    story.append(
        Paragraph(
            "During development, AI coding assistants were used to structure the implementation plan, "
            "draft initial module code, review dependency choices, and create documentation. "
            "All technical decisions were manually validated and adjusted. "
            "The final code was tested, organized, and refined for readability and maintainability.",
            normal_style,
        )
    )

    doc.build(story)
    print(f"PDF generated successfully: {output_path}")


if __name__ == "__main__":
    output_file = (
        f"{NAME} - {POSITION}.pdf".replace(" – ", " - ")
    )
    create_pdf(output_file)
