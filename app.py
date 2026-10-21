
from pathlib import Path

import streamlit as st

from src.transcript.services.media import transcrever_media
from src.transcript.services.pdf_chat import criar_chain_conversa
from src.transcript.services.analysis_service import analisar_transcricao


PROJECT_ROOT = Path(__file__).resolve().parent
PDF_FOLDER = PROJECT_ROOT / "files"


def exibir_analise(analise):
    """Exibe os campos da análise estruturada."""

    st.subheader("Resumo")
    st.write(analise.resumo)

    st.subheader("Tópicos principais")
    if analise.topicos_principais:
        for topico in analise.topicos_principais:
            st.markdown(f"- {topico}")
    else:
        st.info("Nenhum tópico identificado.")

    st.subheader("Decisões")
    if analise.decisoes:
        for decisao in analise.decisoes:
            st.markdown(f"- {decisao}")
    else:
        st.info("Nenhuma decisão identificada.")

    st.subheader("Tarefas")
    if analise.tarefas:
        for tarefa in analise.tarefas:
            responsavel = tarefa.responsavel or "Não identificado"
            st.markdown(f"- **Tarefa:** {tarefa.descricao}")
            st.caption(f"Responsável: {responsavel}")
    else:
        st.info("Nenhuma tarefa identificada.")

    st.subheader("Dúvidas em aberto")
    if analise.duvidas_em_aberto:
        for duvida in analise.duvidas_em_aberto:
            st.markdown(f"- {duvida}")
    else:
        st.info("Nenhuma dúvida em aberto identificada.")


def processar_midia(arquivo, prompt=None):
    """Executa a transcrição e a análise estruturada."""
    with st.spinner("Transcrevendo arquivo..."):
        transcricao = transcrever_media(arquivo, prompt)

    if not transcricao or not str(transcricao).strip():
        st.warning("Não foi possível obter uma transcrição desse arquivo.")
        return

    st.success("Transcrição concluída!")

    with st.expander("Ver transcrição completa", expanded=True):
        st.text_area(
            "Texto transcrito",
            value=str(transcricao),
            height=250,
            disabled=True,
            key=f"transcricao_{arquivo.name}",
        )

    with st.spinner("Analisando o conteúdo..."):
        analise = analisar_transcricao(str(transcricao))

    st.success("Análise concluída!")
    exibir_analise(analise)


def pagina_transcricao():
    """Interface para transcrição e análise de áudio e vídeo."""
    st.subheader("Transcreva e analise áudios e vídeos")

    tab_video, tab_audio = st.tabs(["Vídeo", "Áudio"])

    with tab_video:
        prompt_video = st.text_input(
            "Contexto opcional para a transcrição",
            key="video_prompt",
        )

        arquivo_video = st.file_uploader(
            "Adicione um vídeo",
            type=["mp4", "mov"],
            key="video_file",
        )

        if arquivo_video is not None and st.button(
            "Transcrever e analisar vídeo",
            key="transcribe_video",
        ):
            try:
                processar_midia(arquivo_video, prompt_video)
            except Exception:
                st.error(
                    "Não foi possível processar o vídeo. "
                    "Verifique o arquivo e tente novamente."
                )
                st.exception(None)

    with tab_audio:
        prompt_audio = st.text_input(
            "Contexto opcional para a transcrição",
            key="audio_prompt",
        )

        arquivo_audio = st.file_uploader(
            "Adicione um áudio",
            type=["mp3", "m4a"],
            key="audio_file",
        )

        if arquivo_audio is not None and st.button(
            "Transcrever e analisar áudio",
            key="transcribe_audio",
        ):
            try:
                processar_midia(arquivo_audio, prompt_audio)
            except Exception:
                st.error(
                    "Não foi possível processar o áudio. "
                    "Verifique o arquivo e tente novamente."
                )
                st.exception(None)


def inicializar_chat():
    """Cria a cadeia de conversa com os PDFs enviados."""
    with st.spinner("Processando PDFs e inicializando o chat..."):
        chain = criar_chain_conversa(PDF_FOLDER)

    st.session_state["chain"] = chain
    st.success("Chat com PDFs inicializado!")


def salvar_pdfs(arquivos_pdf):
    """Salva os PDFs enviados na pasta do projeto."""
    PDF_FOLDER.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos_pdf:
        nome = Path(arquivo.name).name

        if nome.lower().endswith(".pdf"):
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

    if arquivos_pdf and st.button("Salvar PDFs", key="save_pdfs"):
        try:
            salvar_pdfs(arquivos_pdf)
            st.success("PDFs salvos com sucesso.")
        except OSError:
            st.error("Não foi possível salvar os PDFs.")
            st.exception(None)

    quantidade_pdfs = len(list(PDF_FOLDER.glob("*.pdf")))
    st.caption(f"PDFs disponíveis: {quantidade_pdfs}")

    if st.button("Inicializar / atualizar chat", key="init_pdf_chat"):
        if quantidade_pdfs == 0:
            st.warning("Adicione pelo menos um PDF antes de inicializar.")
        else:
            try:
                inicializar_chat()
            except Exception:
                st.error("Não foi possível inicializar o chat PDF.")
                st.exception(None)

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

        except Exception:
            st.error("Não foi possível consultar os documentos.")
            st.exception(None)


def main():
    st.set_page_config(
        page_title="Transcript AI",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("🎙️ Transcript AI")
    st.markdown(
        "Transcreva áudios e vídeos, gere análises estruturadas "
        "e converse com seus documentos PDF."
    )

    tab_transcricao, tab_pdf = st.tabs(["Áudio e vídeo", "Chat PDF"])

    with tab_transcricao:
        pagina_transcricao()

    with tab_pdf:
        pagina_chat_pdf()


if __name__ == "__main__":
    main()