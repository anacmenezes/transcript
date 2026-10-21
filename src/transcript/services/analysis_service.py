
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.transcript.core.config import get_settings
from src.transcript.models.analysis import AnaliseTranscricao


def analisar_transcricao(transcricao: str) -> AnaliseTranscricao:
    """Gera uma análise estruturada a partir de uma transcrição."""

    if not transcricao or not transcricao.strip():
        raise ValueError("A transcrição não pode estar vazia.")

    settings = get_settings()

    modelo = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0,
    )

    modelo_estruturado = modelo.with_structured_output(
        AnaliseTranscricao
    )

    mensagens = [
        SystemMessage(
            content=(
                "Você é um assistente especializado em analisar transcrições. "
                "Responda em português do Brasil e siga o schema fornecido. "
                "Use somente informações presentes na transcrição. "
                "Não invente decisões, tarefas ou responsáveis. "
                "Quando uma informação não existir, use listas vazias "
                "ou None, conforme o campo."
            )
        ),
        HumanMessage(
            content=f"Analise a transcrição abaixo:\n\n{transcricao}"
        ),
    ]

    return modelo_estruturado.invoke(mensagens)