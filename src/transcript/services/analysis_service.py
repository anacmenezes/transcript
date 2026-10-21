
import logging

from langchain_openai import ChatOpenAI

from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import AnalysisError
from src.transcript.models.analysis import AnaliseTranscricao

logger = logging.getLogger(__name__)


def analisar_transcricao(transcricao: str) -> AnaliseTranscricao:
    """Gera e valida uma análise estruturada da transcrição."""

    if not isinstance(transcricao, str) or not transcricao.strip():
        raise AnalysisError("Não há texto suficiente para analisar.")

    try:
        settings = get_settings()

        modelo = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0,
            max_retries=2,
            timeout=90.0,
        )

        modelo_estruturado = modelo.with_structured_output(
            AnaliseTranscricao
        )

        prompt = [
            (
                "system",
                "Analise transcrições em português do Brasil. "
                "Use exclusivamente informações presentes no texto. "
                "Não invente decisões, tarefas ou responsáveis. "
                "Quando não houver informação para uma lista, retorne "
                "uma lista vazia. Quando o responsável não for informado, "
                "retorne None.",
            ),
            ("human", f"Analise esta transcrição:\n\n{transcricao}"),
        ]

        resultado = modelo_estruturado.invoke(prompt)

        if not isinstance(resultado, AnaliseTranscricao):
            raise AnalysisError(
                "O modelo não retornou uma análise no formato esperado."
            )

        return resultado

    except AnalysisError:
        raise
    except Exception as error:
        logger.exception("Falha ao gerar a análise estruturada.")
        raise AnalysisError(
            "Não foi possível analisar a transcrição. "
            "Tente novamente mais tarde."
        ) from error