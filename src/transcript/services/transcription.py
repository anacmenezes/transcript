
import logging

from openai import OpenAI, APIError, APIConnectionError, RateLimitError

from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import (
    InvalidFileError,
    TranscriptionError,
)

logger = logging.getLogger(__name__)


def transcrever_audio(file_audio, prompt=None):
    """Envia um arquivo de áudio à OpenAI e retorna a transcrição."""

    if file_audio is None:
        raise InvalidFileError("Nenhum arquivo de áudio foi fornecido.")

    nome = getattr(file_audio, "name", "")
    if not nome:
        raise InvalidFileError("O arquivo de áudio não possui nome.")

    try:
        settings = get_settings()
        client = OpenAI(
            api_key=settings.openai_api_key,
            max_retries=2,
            timeout=120.0,
        )

        file_audio.seek(0)

        resultado = client.audio.transcriptions.create(
            model="whisper-1",
            language="pt",
            response_format="text",
            file=file_audio,
            prompt=prompt or None,
        )

        if not resultado or not str(resultado).strip():
            raise TranscriptionError(
                "A API não retornou uma transcrição válida."
            )

        return resultado

    except InvalidFileError:
        raise
    except TranscriptionError:
        raise
    except (APIConnectionError, RateLimitError, APIError) as error:
        logger.exception("Falha na API durante a transcrição.")
        raise TranscriptionError(
            "O serviço de transcrição está temporariamente indisponível. "
            "Tente novamente em alguns instantes."
        ) from error
    except Exception as error:
        logger.exception("Erro inesperado durante a transcrição.")
        raise TranscriptionError(
            "Não foi possível transcrever o arquivo."
        ) from error