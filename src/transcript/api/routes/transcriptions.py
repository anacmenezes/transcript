
import logging
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.transcript.core.exceptions import (
    InvalidFileError,
    TranscriptAIError,
    TranscriptionError,
)
from src.transcript.db.models import TranscriptionRecord
from src.transcript.db.session import get_db
from src.transcript.models.transcription import (
    TranscriptionListResponse,
    TranscriptionResponse,
)
from src.transcript.services.media import transcrever_media


logger = logging.getLogger(__name__)

router = APIRouter()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


@router.post("", response_model=TranscriptionResponse, status_code=201)
async def criar_transcricao(
    file: UploadFile = File(..., description="Arquivo MP3, M4A, MP4 ou MOV"),
    db: Session = Depends(get_db),
):
    filename = Path(file.filename or "").name

    if not filename or filename in {".", ".."}:
        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado não possui um nome válido.",
        )

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="O arquivo enviado está vazio.",
            )

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="O arquivo excede o limite de 100 MB.",
            )

        # Adapta o arquivo HTTP à interface esperada pelo serviço existente.
        media_file = BytesIO(content)
        media_file.name = filename

        transcript_text = transcrever_media(media_file)

        record = TranscriptionRecord(
            filename=filename,
            media_type=Path(filename).suffix.lower().lstrip("."),
            transcript_text=str(transcript_text),
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record

    except HTTPException:
        raise
    except InvalidFileError as error:
        raise HTTPException(
            status_code=415,
            detail=str(error),
        ) from error
    except TranscriptionError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
    except TranscriptAIError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error
    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Erro ao salvar a transcrição no banco.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar a transcrição.",
        ) from error
    except Exception as error:
        db.rollback()
        logger.exception("Erro inesperado ao criar transcrição.")
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro inesperado ao processar a transcrição.",
        ) from error
    finally:
        await file.close()


@router.get("", response_model=TranscriptionListResponse)
def listar_transcricoes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        total = db.scalar(
            select(func.count()).select_from(TranscriptionRecord)
        ) or 0

        records = db.scalars(
            select(TranscriptionRecord)
            .order_by(TranscriptionRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        return {"items": records, "total": total}

    except SQLAlchemyError as error:
        logger.exception("Erro ao listar transcrições.")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar as transcrições.",
        ) from error


@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def buscar_transcricao(
    transcription_id: int,
    db: Session = Depends(get_db),
):
    record = db.get(TranscriptionRecord, transcription_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Transcrição não encontrada.",
        )

    return record