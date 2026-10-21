
import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.transcript.core.exceptions import (
    ChatInitializationError,
    ChatQueryError,
    DocumentProcessingError,
)
from src.transcript.services.pdf_chat import (
    criar_chain_conversa,
    consultar_documentos,
)

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_PDF_SIZE = 20 * 1024 * 1024  # 20 MB por arquivo
MAX_PDFS = 10


class PerguntaRequest(BaseModel):
    pergunta: str = Field(min_length=1, max_length=5000)


class FonteResponse(BaseModel):
    arquivo: str
    pagina: int | None = None


class PerguntaResponse(BaseModel):
    sessao_id: str
    resposta: str
    fontes: list[FonteResponse]


# Sessões temporárias em memória. Não compartilhar entre usuários.
sessoes: dict[str, dict] = {}


@router.post("/sessoes", status_code=201)
async def criar_sessao_pdf(
    file: Annotated[
        UploadFile,
        File(description="Selecione um arquivo PDF"),
    ],
):
    temp_dir = tempfile.mkdtemp(prefix="transcript_pdf_")
    pasta = Path(temp_dir)

    try:
        nome = Path(file.filename or "").name

        if not nome or Path(nome).suffix.lower() != ".pdf":
            raise HTTPException(
                status_code=415,
                detail="O arquivo deve estar no formato PDF.",
            )

        conteudo = await file.read()

        if not conteudo:
            raise HTTPException(
                status_code=400,
                detail=f"O arquivo {nome} está vazio.",
            )

        if len(conteudo) > MAX_PDF_SIZE:
            raise HTTPException(
                status_code=413,
                detail="O arquivo excede o limite de 20 MB.",
            )

        destino = pasta / nome
        destino.write_bytes(conteudo)

        chain = criar_chain_conversa(pasta)
        sessao_id = str(uuid.uuid4())

        sessoes[sessao_id] = {
            "chain": chain,
            "pasta": temp_dir,
        }

        return {
            "sessao_id": sessao_id,
            "arquivos": [destino.name],
            "mensagem": "Chat com PDFs inicializado.",
        }

    except HTTPException:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    except (
        DocumentProcessingError,
        ChatInitializationError,
    ) as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.exception("Falha ao inicializar a sessão PDF.")
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        logger.exception("Erro inesperado ao criar sessão PDF.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível inicializar o chat com os PDFs.",
        ) from error

    finally:
        await file.close()

@router.post(
    "/sessoes/{sessao_id}/perguntas",
    response_model=PerguntaResponse,
)
def perguntar_pdf(sessao_id: str, request: PerguntaRequest):
    sessao = sessoes.get(sessao_id)

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou já encerrada.",
        )

    try:
        resultado = consultar_documentos(
            sessao["chain"],
            request.pergunta,
        )

        fontes = []
        for documento in resultado.get("source_documents", []):
            metadata = documento.metadata or {}
            fonte = FonteResponse(
                arquivo=Path(str(metadata.get("source", "Documento"))).name,
                pagina=metadata.get("page"),
            )
            if fonte not in fontes:
                fontes.append(fonte)

        return PerguntaResponse(
            sessao_id=sessao_id,
            resposta=resultado["answer"],
            fontes=fontes,
        )

    except ChatQueryError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        logger.exception("Falha ao consultar a sessão PDF.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar os documentos.",
        ) from error


@router.delete("/sessoes/{sessao_id}", status_code=204)
def encerrar_sessao_pdf(sessao_id: str):
    sessao = sessoes.pop(sessao_id, None)

    if sessao is None:
        raise HTTPException(
            status_code=404,
            detail="Sessão não encontrada ou já encerrada.",
        )

    shutil.rmtree(sessao["pasta"], ignore_errors=True)