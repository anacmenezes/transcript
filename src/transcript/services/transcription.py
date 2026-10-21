
import logging

from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError, AuthenticationError
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
        file_audio.seek(0)
    except (AttributeError, OSError, ValueError) as error:
        raise InvalidFileError(
            "Não foi possível acessar o arquivo de áudio."
        ) from error

    try:
        settings = get_settings()

    except (ValueError, OSError) as error:
        logger.exception("Falha ao carregar as configurações.")
        raise TranscriptionError(
            "A configuração da transcrição está incompleta. "
            "Verifique as variáveis de ambiente."
        ) from error

    try:
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

        return str(resultado)

    except InvalidFileError:
        raise

    except TranscriptionError:
        raise

    except AuthenticationError as error:
        logger.exception(
            "Falha de autenticação na API de transcrição."
        )
        raise TranscriptionError(
            "Não foi possível autenticar na OpenAI. "
            "Verifique a chave da API."
        ) from error

    except RateLimitError as error:
        logger.exception(
            "Limite de requisições ou cota da API atingido."
        )
        raise TranscriptionError(
            "A API da OpenAI está limitando as requisições "
            "ou a cota disponível foi atingida. Tente novamente "
            "mais tarde e verifique sua conta."
        ) from error

    except (APIConnectionError, OpenAIError) as error:
        logger.exception(
            "Falha na API durante a transcrição."
        )
        raise TranscriptionError(
            "O serviço de transcrição está indisponível "
            "ou ocorreu uma falha na API. Tente novamente."
        ) from error

    except Exception as error:
        logger.exception(
            "Erro inesperado durante a transcrição."
        )
        raise TranscriptionError(
            "Não foi possível transcrever o arquivo."
        ) from error