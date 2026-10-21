
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.transcript.core.exceptions import AnalysisError
from src.transcript.db.models import AnalysisRecord, TranscriptionRecord
from src.transcript.db.session import get_db
from src.transcript.models.analysis_record import (
    AnalysisListResponse,
    AnalysisRecordResponse,
)
from src.transcript.services.analysis_service import analisar_transcricao


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/{transcription_id}/analise",
    response_model=AnalysisRecordResponse,
    status_code=201,
)
def criar_analise(
    transcription_id: int,
    db: Session = Depends(get_db),
):
    transcricao = db.get(TranscriptionRecord, transcription_id)

    if transcricao is None:
        raise HTTPException(
            status_code=404,
            detail="Transcrição não encontrada.",
        )

    try:
        resultado = analisar_transcricao(transcricao.transcript_text)

        registro = AnalysisRecord(
            transcription_id=transcricao.id,
            result=resultado.model_dump(mode="json"),
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro

    except AnalysisError as error:
        db.rollback()
        logger.exception("Falha ao analisar a transcrição %s.", transcription_id)
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    except SQLAlchemyError as error:
        db.rollback()
        logger.exception(
            "Falha ao salvar a análise da transcrição %s.",
            transcription_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar a análise.",
        ) from error


@router.get(
    "/{transcription_id}/analise",
    response_model=AnalysisRecordResponse,
)
def buscar_ultima_analise(
    transcription_id: int,
    db: Session = Depends(get_db),
):
    transcricao = db.get(TranscriptionRecord, transcription_id)

    if transcricao is None:
        raise HTTPException(
            status_code=404,
            detail="Transcrição não encontrada.",
        )

    registro = db.scalar(
        select(AnalysisRecord)
        .where(AnalysisRecord.transcription_id == transcription_id)
        .order_by(
            AnalysisRecord.created_at.desc(),
            AnalysisRecord.id.desc(),
        )
        .limit(1)
    )

    if registro is None:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma análise encontrada para esta transcrição.",
        )

    return registro


@router.get(
    "/{transcription_id}/analises",
    response_model=AnalysisListResponse,
)
def listar_analises(
    transcription_id: int,
    db: Session = Depends(get_db),
):
    transcricao = db.get(TranscriptionRecord, transcription_id)

    if transcricao is None:
        raise HTTPException(
            status_code=404,
            detail="Transcrição não encontrada.",
        )

    try:
        total = db.scalar(
            select(func.count())
            .select_from(AnalysisRecord)
            .where(AnalysisRecord.transcription_id == transcription_id)
        ) or 0

        registros = db.scalars(
            select(AnalysisRecord)
            .where(AnalysisRecord.transcription_id == transcription_id)
            .order_by(
                AnalysisRecord.created_at.desc(),
                AnalysisRecord.id.desc(),
            )
        ).all()

        return {"items": registros, "total": total}

    except SQLAlchemyError as error:
        logger.exception(
            "Falha ao listar análises da transcrição %s.",
            transcription_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar as análises.",
        ) from error