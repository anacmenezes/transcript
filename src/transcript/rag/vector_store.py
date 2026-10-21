
import logging

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import ChatInitializationError

logger = logging.getLogger(__name__)


def criar_vector_store(documentos):
    """Gera embeddings e cria o índice vetorial FAISS."""

    if not documentos:
        raise ChatInitializationError(
            "Não há trechos para indexar."
        )

    try:
        settings = get_settings()

        embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            max_retries=2,
            request_timeout=60,
        )

        return FAISS.from_documents(
            documents=documentos,
            embedding=embeddings,
        )

    except ChatInitializationError:
        raise

    except Exception as error:
        logger.exception(
            "Falha ao criar o índice vetorial."
        )
        raise ChatInitializationError(
            "Não foi possível indexar os documentos. "
            "Verifique a conexão com o serviço de embeddings."
        ) from error