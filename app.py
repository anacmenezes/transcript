
from pathlib import Path

import streamlit as st

from src.transcript.services.media import transcrever_media
from src.transcript.services.pdf_chat import criar_chain_conversa


PROJECT_ROOT = Path(__file__).resolve().parent
PDF_FOLDER = PROJECT_ROOT / "files"


def inicializar_chat():
    """Cria a cadeia de conversa com os PDFs enviados."""
    try:
        with st.spinner("Processando PDFs e inicializando o chat..."):
            chain = criar_chain_conversa(PDF_FOLDER)

        st.session_state["chain"] = chain
        st.session_state["pdf_folder"] = str(PDF_FOLDER)
        st.success("Chat com PDFs inicializado!")

    except Exception as error:
        st.error(f"Não foi possível inicializar o chat: {error}")


def pagina_transcricao():
    """Interface de transcrição de áudio e vídeo."""
    st.subheader("Transcreva áudios e vídeos")

    tab_video, tab_audio = st.tabs(["Vídeo", "Áudio"])

    with tab_video:
        st.markdown("Transcreva o áudio de um vídeo.")

        prompt_video = st.text_input(
            "Digite seu prompt para o vídeo",
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
                    st.error(f"Erro ao transcrever o vídeo: {error}")

    with tab_audio:
        st.markdown("Transcreva seu arquivo de áudio.")

        prompt_audio = st.text_input(
            "Digite seu prompt para o áudio",
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
                    st.error(f"Erro ao transcrever o áudio: {error}")


def salvar_pdfs(arquivos_pdf):
    """Salva os PDFs enviados na pasta do projeto."""
    PDF_FOLDER.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos_pdf:
        nome = Path(arquivo.name).name

        if not nome.lower().endswith(".pdf"):
            continue

        destino = PDF_FOLDER / nome
        destino.write_bytes(arquivo.getvalue())


def pagina_chat_pdf():
    """Interface para conversar com documentos PDF."""
    st.subheader("Converse com seus documentos")

    PDF_FOLDER.mkdir(parents=True, exist_ok=True)

    arquivos_pdf = st.file_uploader(
        "Adicione arquivos PDF",
        type=["pdf"],
        accept_multiple_files=True,
        key="pdf_upload",
    )

    if arquivos_pdf:
        if st.button("Salvar PDFs", key="save_pdfs"):
            try:
                salvar_pdfs(arquivos_pdf)
                st.success(f"{len(arquivos_pdf)} arquivo(s) salvo(s).")
            except OSError as error:
                st.error(f"Não foi possível salvar os PDFs: {error}")

    quantidade_pdfs = len(list(PDF_FOLDER.glob("*.pdf")))

    st.caption(f"PDFs disponíveis na pasta: {quantidade_pdfs}")

    if st.button("Inicializar / atualizar chat", key="init_pdf_chat"):
        if quantidade_pdfs == 0:
            st.warning("Adicione pelo menos um PDF antes de inicializar.")
        else:
            inicializar_chat()

    chain = st.session_state.get("chain")

    if chain is None:
        st.info("Salve seus PDFs e inicialize o chat para começar.")
        return

    pergunta = st.chat_input(
        "Faça uma pergunta sobre seus documentos",
        key="pdf_question",
    )

    if pergunta:
        try:
            with st.spinner("Buscando informações nos documentos..."):
                resposta = chain.invoke({"question": pergunta})

            st.markdown("**Resposta**")
            st.write(resposta.get("answer", "Não foi possível gerar a resposta."))

            fontes = resposta.get("source_documents", [])
            if fontes:
                with st.expander("Consultar fontes"):
                    for indice, documento in enumerate(fontes, start=1):
                        origem = documento.metadata.get("source", "Documento")
                        pagina = documento.metadata.get("page")

                        st.markdown(f"**Fonte {indice}: {origem}**")
                        if pagina is not None:
                            st.caption(f"Página: {pagina + 1}")
                        st.write(documento.page_content[:1000])

        except Exception as error:
            st.error(f"Erro ao consultar os documentos: {error}")


def main():
    st.set_page_config(
        page_title="Transcript AI",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("🎙️ Transcript AI")
    st.markdown(
        "Transcreva áudios e vídeos ou converse com seus documentos PDF."
    )

    tab_transcricao, tab_pdf = st.tabs(
        ["Áudio e vídeo", "Chat PDF"]
    )

    with tab_transcricao:
        pagina_transcricao()

    with tab_pdf:
        pagina_chat_pdf()


if __name__ == "__main__":
    main()