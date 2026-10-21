
import logging
from pathlib import Path

import streamlit as st

from src.transcript.core.exceptions import (
    TranscriptAIError,
    AnalysisError,
    ChatQueryError,
    InvalidFileError,
    TranscriptionError,
)
from src.transcript.services.analysis_service import analisar_transcricao
from src.transcript.services.media import transcrever_media
from src.transcript.services.pdf_chat import (
    criar_chain_conversa,
    consultar_documentos,
)

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
PDF_FOLDER = PROJECT_ROOT / "files"


def exibir_analise(analise):
    st.subheader("Resumo")
    st.write(analise.resumo)

    secoes = [
        ("Tópicos principais", analise.topicos_principais),
        ("Decisões", analise.decisoes),
        ("Dúvidas em aberto", analise.duvidas_em_aberto),
    ]

    for titulo, itens in secoes:
        st.subheader(titulo)
        if itens:
            for item in itens:
                st.markdown(f"- {item}")
        else:
            st.caption("Nenhum item identificado.")

    st.subheader("Tarefas")
    if analise.tarefas:
        for tarefa in analise.tarefas:
            st.markdown(f"- **Tarefa:** {tarefa.descricao}")
            st.caption(
                f"Responsável: {tarefa.responsavel or 'Não identificado'}"
            )
    else:
        st.caption("Nenhuma tarefa identificada.")

def executar_transcricao(arquivo, prompt=None):
    """Transcreve a mídia e guarda o texto para uso posterior."""

    try:
        with st.spinner("Transcrevendo arquivo..."):
            transcricao = transcrever_media(arquivo, prompt)

        if not transcricao or not str(transcricao).strip():
            raise TranscriptionError(
                "Não foi possível obter uma transcrição desse arquivo."
            )

        st.session_state["transcricao_atual"] = str(transcricao)
        st.session_state["nome_arquivo_transcricao"] = arquivo.name
        st.session_state["analise_atual"] = None

        st.success("Transcrição concluída!")

    except TranscriptAIError as error:
        logger.warning("Falha na transcrição: %s", error)
        st.error(str(error))

    except Exception:
        logger.exception("Erro inesperado na transcrição.")
        st.error(
            "Ocorreu um erro inesperado ao transcrever o arquivo. "
            "Tente novamente."
        )

def executar_analise():
    """Analisa a transcrição salva sem chamar a API de transcrição."""

    transcricao = st.session_state.get("transcricao_atual")

    if not transcricao:
        st.warning("Faça uma transcrição antes de solicitar a análise.")
        return

    try:
        with st.spinner("Analisando o conteúdo..."):
            analise = analisar_transcricao(transcricao)

        st.session_state["analise_atual"] = analise
        st.success("Análise concluída!")

    except AnalysisError:
        logger.exception("Falha na análise da transcrição.")
        st.error(
            "A transcrição foi preservada, mas a análise falhou. "
            "Você pode tentar novamente."
        )

    except TranscriptAIError as error:
        logger.exception("Falha no processamento da análise.")
        st.error(
            "A transcrição foi preservada, mas não foi possível "
            f"concluir a análise: {error}"
        )

    except Exception:
        logger.exception("Erro inesperado durante a análise.")
        st.error(
            "A transcrição foi preservada, mas ocorreu um erro "
            "inesperado na análise. Tente novamente."
        )

def inicializar_chat():
    """Inicializa a cadeia RAG com os PDFs disponíveis."""

    try:
        with st.spinner("Processando PDFs e inicializando o chat..."):
            chain = criar_chain_conversa(PDF_FOLDER)

        st.session_state["chain"] = chain
        st.success("Chat com PDFs inicializado!")

    except TranscriptAIError as error:
        st.error(str(error))
    except Exception:
        logger.exception("Erro inesperado ao inicializar o chat PDF.")
        st.error("Não foi possível inicializar o chat PDF.")

def salvar_pdfs(arquivos_pdf):
    """Salva os PDFs enviados na pasta do projeto."""

    PDF_FOLDER.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos_pdf:
        nome = Path(arquivo.name).name

        if not nome.lower().endswith(".pdf"):
            continue

        if not arquivo.getvalue():
            raise InvalidFileError(
                f"O arquivo '{nome}' está vazio."
            )

        destino = PDF_FOLDER / nome
        destino.write_bytes(arquivo.getvalue())

def pagina_transcricao():
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
            "Transcrever vídeo",
            key="transcribe_video",
        ):
            executar_transcricao(arquivo_video, prompt_video)

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
            "Transcrever áudio",
            key="transcribe_audio",
        ):
            executar_transcricao(arquivo_audio, prompt_audio)

    transcricao = st.session_state.get("transcricao_atual")
    nome_arquivo = st.session_state.get(
        "nome_arquivo_transcricao",
        "Arquivo transcrito",
    )

    if transcricao:
        st.divider()
        st.subheader(f"Transcrição: {nome_arquivo}")

        st.text_area(
            "Texto transcrito",
            value=transcricao,
            height=250,
            disabled=True,
            key="transcricao_exibida",
        )

        if st.button(
            "Analisar transcrição",
            key="analisar_transcricao",
        ):
            executar_analise()

        analise = st.session_state.get("analise_atual")

        if analise is not None:
            exibir_analise(analise)

def pagina_chat_pdf():
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
        except TranscriptAIError as error:
            st.error(str(error))
        except OSError:
            logger.exception("Erro ao salvar PDFs.")
            st.error("Não foi possível salvar os arquivos.")

    quantidade_pdfs = len(list(PDF_FOLDER.glob("*.pdf")))
    st.caption(f"PDFs disponíveis: {quantidade_pdfs}")

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
                resposta = consultar_documentos(chain, pergunta)

            st.markdown("**Resposta**")
            st.write(resposta["answer"])

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

        except ChatQueryError as error:
            st.error(str(error))
        except TranscriptAIError as error:
            st.error(str(error))
        except Exception:
            logger.exception("Erro inesperado ao consultar o chat PDF.")
            st.error("Ocorreu um erro inesperado ao consultar os documentos.")

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