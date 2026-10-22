
import pytest
from langchain_core.documents import Document

from io import BytesIO
from unittest.mock import MagicMock, patch

from src.transcript.core.exceptions import (
    AnalysisError,
    ChatQueryError,
    DocumentProcessingError,
    InvalidFileError,
)
from src.transcript.rag.splitter import dividir_documentos
from src.transcript.services.analysis_service import analisar_transcricao
from src.transcript.services.media import transcrever_media
from src.transcript.services.pdf_chat import consultar_documentos
from src.transcript.services.transcription import transcrever_audio
from src.transcript.services import transcription

def test_transcricao_rejeita_arquivo_ausente():
    with pytest.raises(InvalidFileError):
        transcrever_audio(None)


def test_media_rejeita_arquivo_ausente():
    with pytest.raises(InvalidFileError):
        transcrever_media(None)


def test_analise_rejeita_texto_vazio():
    with pytest.raises(AnalysisError):
        analisar_transcricao("   ")


def test_chat_rejeita_pergunta_vazia():
    with pytest.raises(ChatQueryError):
        consultar_documentos(None, "   ")


def test_chat_rejeita_chain_ausente():
    with pytest.raises(ChatQueryError):
        consultar_documentos(None, "Qual é o resumo?")


def test_divisao_rejeita_lista_vazia():
    with pytest.raises(DocumentProcessingError):
        dividir_documentos([])


def test_divisao_cria_trechos_com_metadados():
    documentos = [
        Document(
            page_content="Este é um documento de teste sobre reuniões.",
            metadata={
                "source": "C:/documentos/reuniao.pdf",
                "page": 0,
            },
        )
    ]

    trechos = dividir_documentos(documentos)

    assert trechos
    assert trechos[0].metadata["source"] == "reuniao.pdf"
    assert trechos[0].metadata["doc_id"] == 0
    assert "reuniões" in trechos[0].page_content


def test_transcricao_audio_com_sucesso():
    from io import BytesIO
    from unittest.mock import patch

    from src.transcript.services import transcription

    arquivo = BytesIO(b"audio de teste")
    arquivo.name = "reuniao.mp3"

    texto_esperado = "Esta é a transcrição da reunião."

    with patch(
        "src.transcript.services.transcription.OpenAI"
    ) as openai_mock:
        cliente_mock = openai_mock.return_value
        cliente_mock.audio.transcriptions.create.return_value = texto_esperado

        resultado = transcription.transcrever_audio(arquivo)

    assert resultado == texto_esperado
    cliente_mock.audio.transcriptions.create.assert_called_once()

def test_analise_transcricao_com_sucesso():
    from unittest.mock import patch

    from src.transcript.models.analysis import AnaliseTranscricao
    from src.transcript.services.analysis_service import analisar_transcricao

    resultado_esperado = AnaliseTranscricao(
        resumo="Reunião sobre o planejamento.",
        topicos=["Planejamento"],
        decisoes=["Revisar o cronograma"],
        tarefas=[],
    )

    with patch(
        "src.transcript.services.analysis_service.ChatOpenAI"
    ) as chat_mock:
        modelo_mock = chat_mock.return_value
        modelo_mock.with_structured_output.return_value.invoke.return_value = (
            resultado_esperado
        )

        resultado = analisar_transcricao(
            "A equipe discutiu o planejamento e decidiu revisar o cronograma."
        )

    assert resultado == resultado_esperado
    modelo_mock.with_structured_output.return_value.invoke.assert_called_once()

def test_consultar_documentos_com_sucesso():
    from unittest.mock import MagicMock

    from src.transcript.services.pdf_chat import consultar_documentos

    chain = MagicMock()
    chain.invoke.return_value = {
        "answer": "A reunião definiu o cronograma do projeto.",
        "source_documents": [],
    }

    resultado = consultar_documentos(
        chain,
        "Qual foi a decisão da reunião?",
    )

    assert resultado["answer"] == (
        "A reunião definiu o cronograma do projeto."
    )
    chain.invoke.assert_called_once_with(
        {"question": "Qual foi a decisão da reunião?"}
    )
