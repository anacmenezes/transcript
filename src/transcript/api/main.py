
from fastapi import FastAPI

from src.transcript.api.routes import analyses, health, pdf_chat, transcriptions

from fastapi import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.transcript.api.middleware import ObservabilityMiddleware
from src.transcript.observability.logging import configure_logging

configure_logging()

app = FastAPI(
    title="Transcript AI API",
    description=(
        "API REST para transcrição de áudio e vídeo, "
        "análise estruturada e consulta de documentos."
    ),
    version="1.0.0",
)

app.add_middleware(ObservabilityMiddleware)

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

app.include_router(health.router)

app.include_router(
    transcriptions.router,
    prefix="/transcricoes",
    tags=["Transcrições"],
)

app.include_router(
    analyses.router,
    prefix="/transcricoes",
    tags=["Análises"],
)
app.include_router(
    pdf_chat.router,
    prefix="/chat-pdf",
    tags=["Chat com PDFs"],
)

@app.get("/health/live", tags=["Saúde"])
def liveness():
    return {"status": "alive", "service": "transcript-ai"}