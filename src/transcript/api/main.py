
from fastapi import FastAPI

from src.transcript.api.routes import analyses, health, pdf_chat, transcriptions


app = FastAPI(
    title="Transcript AI API",
    description=(
        "API REST para transcrição de áudio e vídeo, "
        "análise estruturada e consulta de documentos."
    ),
    version="1.0.0",
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