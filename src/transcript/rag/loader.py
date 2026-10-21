
import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader

from src.transcript.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


def importar_documentos(pasta_pdfs: Path):
    """Carrega o conteúdo textual dos PDFs de uma pasta."""

    if not pasta_pdfs.is_dir():
        raise DocumentProcessingError(
            "A pasta de documentos não existe."
        )

    arquivos_pdf = sorted(pasta_pdfs.glob("*.pdf"))

    if not arquivos_pdf:
        raise DocumentProcessingError(
            "Nenhum arquivo PDF foi encontrado."
        )

    documentos = []

    for arquivo in arquivos_pdf:
        try:
            paginas = PyPDFLoader(str(arquivo)).load()
            documentos.extend(paginas)

        except Exception as error:
            logger.exception(
                "Falha ao carregar PDF: %s",
                arquivo.name,
            )
            raise DocumentProcessingError(
                f"Não foi possível ler o PDF '{arquivo.name}'. "
                "Verifique se o arquivo está íntegro e legível."
            ) from error

    if not any(
        documento.page_content.strip()
        for documento in documentos
    ):
        raise DocumentProcessingError(
            "Os PDFs não contêm texto extraível."
        )

    return documentos