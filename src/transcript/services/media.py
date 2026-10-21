
import logging
import subprocess
import tempfile

import imageio_ffmpeg

from pathlib import Path
from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import (
    InvalidFileError,
    TranscriptionError,
)
from src.transcript.services.transcription import transcrever_audio
from src.transcript.utils.files import garantir_diretorio

logger = logging.getLogger(__name__)

EXTENSOES_VIDEO = {".mov", ".mp4"}
EXTENSOES_AUDIO = {".mp3", ".m4a"}


def transcrever_media(file_media, prompt=None):
    """Transcreve áudio ou extrai o áudio de um vídeo."""

    if file_media is None:
        raise InvalidFileError("Nenhum arquivo foi enviado.")

    nome = getattr(file_media, "name", "")
    if not nome:
        raise InvalidFileError("O arquivo enviado não possui nome.")

    extensao = "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""

    if extensao not in EXTENSOES_VIDEO | EXTENSOES_AUDIO:
        raise InvalidFileError(
            "Formato não suportado. Envie MP3, M4A, MP4 ou MOV."
        )

    try:
        conteudo = file_media.getvalue()
    except (AttributeError, OSError, ValueError) as error:
        raise InvalidFileError("Não foi possível ler o arquivo enviado.") from error

    if not conteudo:
        raise InvalidFileError("O arquivo enviado está vazio.")

    if extensao in EXTENSOES_AUDIO:
        file_media.seek(0)
        return transcrever_audio(file_media, prompt)

    try:
        settings = get_settings()
        garantir_diretorio(settings.temp_dir)

        # Cada execução usa seu próprio diretório temporário.
        with tempfile.TemporaryDirectory(
            prefix="transcript_",
            dir=str(settings.temp_dir),
        ) as diretorio_temporario:
            pasta_temporaria = Path(diretorio_temporario)

            video_path = pasta_temporaria / f"video{extensao}"
            audio_path = pasta_temporaria / "audio.mp3"

            video_path.write_bytes(conteudo)

            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

            comando = [
                ffmpeg_path,
                "-i", str(video_path),
                "-vn",
                "-ac", "2",
                "-ar", "16000",
                "-codec:a", "libmp3lame",
                "-y",
                str(audio_path),
            ]

            subprocess.run(
                comando,
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if not audio_path.is_file() or audio_path.stat().st_size == 0:
                raise TranscriptionError(
                    "Não foi possível extrair áudio válido do vídeo."
                )

            with audio_path.open("rb") as audio_file:
                return transcrever_audio(audio_file, prompt)

    except TranscriptionError:
        raise

    except subprocess.TimeoutExpired as error:
        logger.warning("Tempo limite excedido ao processar vídeo.")
        raise TranscriptionError(
            "O processamento do vídeo excedeu o tempo limite."
        ) from error

    except subprocess.CalledProcessError as error:
        logger.warning(
            "FFmpeg falhou: %s",
            (error.stderr or "")[-2000:],
        )
        raise TranscriptionError(
            "Não foi possível extrair o áudio. "
            "Verifique se o vídeo é válido e contém áudio."
        ) from error

    except Exception as error:
        logger.exception(
            "Falha inesperada ao processar o vídeo."
        )
        raise TranscriptionError(
            "Ocorreu um erro ao preparar o vídeo para transcrição."
        ) from error