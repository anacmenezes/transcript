
import subprocess

import imageio_ffmpeg

from src.transcript.core.config import get_settings
from src.transcript.services.transcription import transcrever_audio
from src.transcript.utils.files import (
    garantir_diretorio,
    remover_arquivo,
)

settings = get_settings()


def transcrever_media(file_media, prompt=None):
    """Transcreve um áudio ou extrai o áudio de um vídeo."""

    if file_media is None:
        return None

    garantir_diretorio(settings.temp_dir)

    nome_arquivo = file_media.name.lower()
    eh_video = nome_arquivo.endswith((".mov", ".mp4"))

    video_extension = (
        ".mov" if nome_arquivo.endswith(".mov") else ".mp4"
    )
    audio_extension = (
        ".m4a" if nome_arquivo.endswith(".m4a") else ".mp3"
    )

    video_path = settings.temp_dir / f"video{video_extension}"
    audio_path = settings.temp_dir / f"audio{audio_extension}"

    if not eh_video:
        return transcrever_audio(file_media, prompt)

    try:
        with open(video_path, "wb") as destination:
            destination.write(file_media.getvalue())

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
        )

        with open(audio_path, "rb") as audio_file:
            return transcrever_audio(audio_file, prompt)

    except subprocess.CalledProcessError as error:
        detalhe = error.stderr[-2000:] if error.stderr else str(error)
        raise RuntimeError(
            f"Não foi possível extrair o áudio do vídeo: {detalhe}"
        ) from error

    finally:
        remover_arquivo(audio_path)
        remover_arquivo(video_path)