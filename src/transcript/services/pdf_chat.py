
import logging
from pathlib import Path

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import (
    ChatInitializationError,
    ChatQueryError,
    DocumentProcessingError,
)
from src.transcript.rag.loader import importar_documentos
from src.transcript.rag.splitter import dividir_documentos
from src.transcript.rag.vector_store import criar_vector_store
from src.transcript.rag.retriever import criar_retriever

logger = logging.getLogger(__name__)


def criar_chain_conversa(pasta_pdfs: Path):
    """Inicializa a cadeia de perguntas e respostas sobre PDFs."""

    try:
        documentos = importar_documentos(pasta_pdfs)
        trechos = dividir_documentos(documentos)
        vector_store = criar_vector_store(trechos)
        retriever = criar_retriever(vector_store, quantidade=4)

        settings = get_settings()

        modelo = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0,
            max_retries=2,
            timeout=90.0,
        )

        memoria = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        return ConversationalRetrievalChain.from_llm(
            llm=modelo,
            retriever=retriever,
            memory=memoria,
            return_source_documents=True,
            verbose=False,
        )

    except (
        DocumentProcessingError,
        ChatInitializationError,
    ):
        raise

    except Exception as error:
        logger.exception(
            "Falha ao inicializar o chat PDF."
        )
        raise ChatInitializationError(
            "Não foi possível inicializar o chat com os documentos."
        ) from error


def consultar_documentos(chain, pergunta: str):
    """Consulta os documentos e devolve a resposta com as fontes."""

    if not isinstance(pergunta, str) or not pergunta.strip():
        raise ChatQueryError(
            "Digite uma pergunta antes de consultar."
        )

    if chain is None:
        raise ChatQueryError(
            "O chat não foi inicializado. Carregue os PDFs primeiro."
        )

    try:
        resultado = chain.invoke({"question": pergunta})

        if (
            not isinstance(resultado, dict)
            or not resultado.get("answer")
        ):
            raise ChatQueryError(
                "O chat não retornou uma resposta válida."
            )

        return resultado

    except ChatQueryError:
        raise

    except Exception as error:
        logger.exception(
            "Falha ao consultar os documentos."
        )
        raise ChatQueryError(
            "Não foi possível responder à pergunta. "
            "Tente novamente mais tarde."
        ) from error