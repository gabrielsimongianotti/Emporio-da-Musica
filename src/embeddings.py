"""Carregamento do PDF de políticas em vector store (FAISS + OpenAI Embeddings)."""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    POLICIES_PDF,
    VECTOR_STORE_DIR,
    logger,
)


def load_policies_vectorstore(
    pdf_path: Path = POLICIES_PDF,
    persist_dir: Path = VECTOR_STORE_DIR,
) -> FAISS:
    """Carrega o PDF de políticas em um vector store FAISS.

    Se o vector store já existir, reutiliza. Caso contrário, lê o PDF,
    divide em chunks, gera embeddings com OpenAI e persiste.
    """
    index_path = persist_dir / "index.faiss"

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        openai_api_key=OPENAI_API_KEY,
    )

    if index_path.exists():
        logger.info("Reutilizando vector store existente em %s", persist_dir)
        return FAISS.load_local(
            str(persist_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    logger.info("Criando novo vector store a partir de %s", pdf_path)

    # Lê o PDF
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    # Divide em chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ";", ",", " ", ""],
    )
    chunks = text_splitter.split_documents(documents)

    # Cria e persiste o vector store
    persist_dir.mkdir(parents=True, exist_ok=True)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(persist_dir))

    logger.info("Vector store criado com sucesso em %s", persist_dir)
    return vectorstore


def search_policies(query: str, k: int = 4) -> list[str]:
    """Busca trechos relevantes do PDF de políticas."""
    vectorstore = load_policies_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
