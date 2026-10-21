
import logging
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.transcript.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


def dividir_documentos(documentos):
    """Divide documentos em trechos menores para recuperação."""

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        trechos = splitter.split_documents(documentos)

        for indice, trecho in enumerate(trechos):
            origem = trecho.metadata.get("source", "")
            trecho.metadata["source"] = Path(origem).name
            trecho.metadata["doc_id"] = indice

        if not trechos:
            raise DocumentProcessingError(
                "Não foi possível criar trechos dos documentos."
            )

        return trechos

    except DocumentProcessingError:
        raise

    except Exception as error:
        logger.exception(
            "Falha ao dividir os documentos em trechos."
        )
        raise DocumentProcessingError(
            "Não foi possível preparar o conteúdo dos PDFs."
        ) from error