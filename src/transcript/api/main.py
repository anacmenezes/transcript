
from fastapi import FastAPI

from src.transcript.api.routes import health, transcriptions


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