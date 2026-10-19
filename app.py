
import streamlit as st

from src.transcript.services.media import transcrever_media


def main():
    st.header("🎙️ App Transcript", divider=True)
    st.subheader("Transcreva áudios e vídeos")

    tab_video, tab_audio = st.tabs(["Vídeo", "Áudio"])

    with tab_video:
        st.markdown("Transcreva o áudio de um vídeo.")

        prompt_video = st.text_input(
            "Digite o seu prompt para o vídeo",
            key="video_prompt",
        )

        file_video = st.file_uploader(
            "Adicione um arquivo de vídeo (.mp4 ou .mov)",
            type=["mp4", "mov"],
            key="video_file",
        )

        if file_video is not None:
            if st.button("Transcrever vídeo", key="transcribe_video"):
                try:
                    with st.spinner(
                        "Extraindo áudio e transcrevendo vídeo..."
                    ):
                        resultado = transcrever_media(
                            file_video,
                            prompt_video,
                        )

                    st.success("Transcrição concluída!")
                    st.write(resultado)

                except Exception as error:
                    st.error(
                        f"Erro ao transcrever o vídeo: {error}"
                    )

    with tab_audio:
        st.markdown("Transcreva seu arquivo de áudio.")

        prompt_audio = st.text_input(
            "Digite o seu prompt para o áudio",
            key="audio_prompt",
        )

        file_audio = st.file_uploader(
            "Adicione um arquivo de áudio (.mp3 ou .m4a)",
            type=["mp3", "m4a"],
            key="audio_file",
        )

        if file_audio is not None:
            if st.button("Transcrever áudio", key="transcribe_audio"):
                try:
                    with st.spinner("Transcrevendo áudio..."):
                        resultado = transcrever_media(
                            file_audio,
                            prompt_audio,
                        )

                    st.success("Transcrição concluída!")
                    st.write(resultado)

                except Exception as error:
                    st.error(
                        f"Erro ao transcrever o áudio: {error}"
                    )


if __name__ == "__main__":
    main()