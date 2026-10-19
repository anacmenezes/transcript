import streamlit as st
import openai
from moviepy.video.io.VideoFileClip import VideoFileClip

# Configuração do cliente OpenAI
openai = openai.Client()

folder_temp = "temp"
file_audio_temp = f"{folder_temp}/audio.mp3"
file_video_temp = f"{folder_temp}/video.mp4"

def transcrever_audio(file_audio, prompt=None):
    """Função para transcrever o áudio usando a API da OpenAI"""
    if file_audio:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            language="pt",
            response_format="text",
            file=file_audio,
            prompt=prompt
        )
        return transcription
    return None

def transcrever_video(file_video, prompt=None):
    """Função para transcrever o vídeo usando a API da OpenAI"""
    if file_video:
        with open(file_video_temp, "wb") as f_video:
            f_video.write(file_video.read())
        video_convert = VideoFileClip(file_video_temp)
        video_convert.audio.write_audiofile(file_audio_temp) # convert arquivo audio
        with open(file_audio_temp, "rb") as file_audio:
            transcription = openai.audio.transcriptions.create(
                model="whisper-1",
                language="pt",
                response_format="text",
                file=file_audio,
                prompt=prompt
            )
        return transcription
    return None

def main():
    """Função principal do app"""
    st.header("🎙️ App Transcript", divider=True)
    st.subheader("Transcreva áudios e vídeos")

    # Criação das abas
    tabs = ["Vídeo", "Áudio"]
    tab_video, tab_audio = st.tabs(tabs)
    
    # Aba Áudio
    with tab_audio:
        st.markdown("Teste áudio")
        prompt_audio = st.text_input("Digite o seu prompt para o áudio", key="audio_prompt")
        file_audio = st.file_uploader("Adicione um arquivo de áudio .mp3", type=["mp3"])
        if file_audio:
            transcricao_audio = transcrever_audio(file_audio, prompt_audio)
            if transcricao_audio:
                st.write(transcricao_audio)
            else:
                st.error("Erro ao transcrever o áudio.")
    
    # Aba Vídeo
    with tab_video:
        st.markdown("Teste vídeo")
        prompt_video = st.text_input("Digite o seu prompt para o vídeo", key="video_prompt")
        file_video = st.file_uploader("Adicione um arquivo de vídeo .mp4", type=["mp4"])
        if file_video:
            transcricao_video = transcrever_video(file_video, prompt_video)
            if transcricao_video:
                st.write(transcricao_video)
            else:
                st.error("Erro ao transcrever o áudio.")

if __name__ == "__main__":
    main()