
from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError
from datetime import datetime, timezone
from unittest.mock import patch

from src.transcript.db.models import TranscriptionRecord
from src.transcript.api.main import app
from src.transcript.db.session import get_db
from src.transcript.models.analysis import AnaliseTranscricao


def test_api_disponibiliza_documentacao(client):
    response = client.get("/docs")
    assert response.status_code == 200

def test_api_retorna_erro_para_rota_inexistente(client):
    response = client.get("/rota-que-nao-existe")
    assert response.status_code == 404

def test_health_retorna_indisponibilidade_quando_banco_falha(client):
    db = MagicMock()
    db.execute.side_effect = OperationalError(
        "SELECT 1", {}, Exception("Banco indisponível")
    )

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health")
        assert response.status_code == 503
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_listar_transcricoes_retorna_lista_vazia(client):
    db = MagicMock()
    db.scalar.return_value = 0
    db.scalars.return_value.all.return_value = []

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/transcricoes")
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_listar_transcricoes_rejeita_limit_acima_do_maximo(client):
    response = client.get("/transcricoes?limit=101")
    assert response.status_code == 422

def test_buscar_transcricao_inexistente_retorna_404(client):
    db = MagicMock()
    db.get.return_value = None

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/transcricoes/999999")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_criar_transcricao_rejeita_arquivo_vazio(client):
    db = MagicMock()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(
            "/transcricoes",
            files={"file": ("audio.mp3", b"", "audio/mpeg")},
        )
        assert response.status_code == 400
        db.add.assert_not_called()
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_criar_sessao_pdf_rejeita_extensao_invalida(client):
    response = client.post(
        "/chat-pdf/sessoes",
        files={"file": ("documento.txt", b"conteudo", "text/plain")},
    )
    assert response.status_code == 415

def test_pergunta_pdf_rejeita_sessao_inexistente(client):
    from src.transcript.api.routes import pdf_chat

    sessao_id = "sessao-inexistente-para-teste"
    pdf_chat.sessoes.pop(sessao_id, None)

    response = client.post(
        f"/chat-pdf/sessoes/{sessao_id}/perguntas",
        json={"pergunta": "Qual é o resumo?"},
    )
    assert response.status_code == 404

def test_encerrar_sessao_pdf_inexistente_retorna_404(client):
    from src.transcript.api.routes import pdf_chat

    sessao_id = "sessao-inexistente-para-teste"
    pdf_chat.sessoes.pop(sessao_id, None)

    response = client.delete(f"/chat-pdf/sessoes/{sessao_id}")
    assert response.status_code == 404

def test_criar_sessao_pdf_rejeita_arquivo_vazio(client):
    response = client.post(
        "/chat-pdf/sessoes",
        files={"file": ("vazio.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400

def test_criar_transcricao_com_sucesso(client):
    registro = TranscriptionRecord(
        id=123,
        filename="reuniao.mp3",
        media_type="mp3",
        transcript_text="A equipe definiu o cronograma.",
        created_at=datetime.now(timezone.utc),
    )

    def salvar_registro():
        return registro

    def override_get_db():
        db = MagicMock()
        db.add.side_effect = lambda obj: None
        db.commit.return_value = None
        db.refresh.side_effect = lambda obj: (
            setattr(obj, "id", registro.id),
            setattr(obj, "created_at", registro.created_at),
        )
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with patch(
            "src.transcript.api.routes.transcriptions.transcrever_media",
            return_value="A equipe definiu o cronograma.",
        ):
            response = client.post(
                "/transcricoes",
                files={
                    "file": (
                        "reuniao.mp3",
                        b"audio de teste",
                        "audio/mpeg",
                    )
                },
            )

        assert response.status_code == 201
        dados = response.json()
        assert dados["filename"] == "reuniao.mp3"
        assert dados["media_type"] == "mp3"
        assert dados["transcript_text"] == (
            "A equipe definiu o cronograma."
        )
        assert dados["id"] == 123
    finally:
        app.dependency_overrides.pop(get_db, None)

def test_criar_analise_com_sucesso(client):
    from datetime import datetime, timezone
    from unittest.mock import MagicMock, patch

    from src.transcript.db.models import AnalysisRecord, TranscriptionRecord

    transcricao = TranscriptionRecord(
        id=123,
        filename="reuniao.mp3",
        media_type="mp3",
        transcript_text="A equipe decidiu revisar o cronograma.",
        created_at=datetime.now(timezone.utc),
    )

    analise = AnaliseTranscricao(
        resumo="A equipe decidiu revisar o cronograma.",
        topicos_principais=["Cronograma"],
        decisoes=["Revisar o cronograma"],
        tarefas=[],
        duvidas_em_aberto=[],
    )

    registro = AnalysisRecord(
        id=456,
        transcription_id=123,
        result=analise.model_dump(mode="json"),
        created_at=datetime.now(timezone.utc),
    )

    db = MagicMock()
    db.get.return_value = transcricao

    def adicionar(obj):
        if isinstance(obj, AnalysisRecord):
            obj.id = registro.id
            obj.created_at = registro.created_at

    db.add.side_effect = adicionar
    db.refresh.side_effect = lambda obj: None

    def override_get_db():
        yield db

    from src.transcript.db.session import get_db
    from src.transcript.api.routes import analyses as analyses_routes

    client_app = client
    from src.transcript.api.main import app

    app.dependency_overrides[get_db] = override_get_db

    try:
        with patch.object(
            analyses_routes,
            "analisar_transcricao",
            return_value=analise,
        ):
            response = client_app.post("/transcricoes/123/analise")

        assert response.status_code == 201
        dados = response.json()
        assert dados["transcription_id"] == 123
        assert dados["result"]["resumo"] == (
            "A equipe decidiu revisar o cronograma."
        )
        db.add.assert_called_once()
        db.commit.assert_called_once()
    finally:
        app.dependency_overrides.pop(get_db, None)
