
import logging
import subprocess

import imageio_ffmpeg

from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import (
    InvalidFileError,
    TranscriptionError,
)
from src.transcript.services.transcription import transcrever_audio
from src.transcript.utils.files import garantir_diretorio, remover_arquivo

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
    except AttributeError as error:
        raise InvalidFileError("Não foi possível ler o arquivo enviado.") from error

    if not conteudo:
        raise InvalidFileError("O arquivo enviado está vazio.")

    if extensao in EXTENSOES_AUDIO:
        try:
            file_media.seek(0)
            return transcrever_audio(file_media, prompt)
        except TranscriptionError:
            raise
        except Exception as error:
            logger.exception("Falha ao transcrever o áudio.")
            raise TranscriptionError(
                "Não foi possível processar o arquivo de áudio."
            ) from error

    settings = get_settings()
    garantir_diretorio(settings.temp_dir)

    video_path = settings.temp_dir / f"video{extensao}"
    audio_path = settings.temp_dir / "audio.mp3"

    try:
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

    except subprocess.TimeoutExpired as error:
        raise TranscriptionError(
            "O processamento do vídeo excedeu o tempo limite."
        ) from error
    except subprocess.CalledProcessError as error:
        logger.warning("FFmpeg falhou: %s", (error.stderr or "")[-2000:])
        raise TranscriptionError(
            "Não foi possível extrair o áudio. "
            "Verifique se o vídeo é válido e contém uma faixa de áudio."
        ) from error
    except (InvalidFileError, TranscriptionError):
        raise
    except OSError as error:
        logger.exception("Erro de arquivo durante o processamento de mídia.")
        raise TranscriptionError(
            "Ocorreu um erro ao processar o arquivo de mídia."
        ) from error
    finally:
        for caminho in (audio_path, video_path):
            try:
                remover_arquivo(caminho)
            except OSError:
                logger.warning("Não foi possível remover o arquivo temporário.")