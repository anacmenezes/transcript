
from openai import OpenAI

from src.transcript.core.config import get_settings


settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)


def transcrever_audio(file_audio, prompt=None):
    if file_audio is None:
        return None

    return client.audio.transcriptions.create(
        model="whisper-1",
        language="pt",
        response_format="text",
        file=file_audio,
        prompt=prompt or None,
    )