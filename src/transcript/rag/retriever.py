
import logging

from src.transcript.core.exceptions import ChatInitializationError

logger = logging.getLogger(__name__)


def criar_retriever(vector_store, quantidade: int = 4):
    """Cria um recuperador de trechos a partir do índice vetorial."""

    if vector_store is None:
        raise ChatInitializationError(
            "O índice vetorial não foi inicializado."
        )

    if quantidade < 1:
        raise ChatInitializationError(
            "A quantidade de trechos deve ser maior que zero."
        )

    try:
        return vector_store.as_retriever(
            search_kwargs={"k": quantidade}
        )

    except Exception as error:
        logger.exception(
            "Falha ao configurar a recuperação de documentos."
        )
        raise ChatInitializationError(
            "Não foi possível preparar a busca nos documentos."
        ) from error