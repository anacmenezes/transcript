import logging
import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

TIMEOUT_API = 180


def requisicao_api(metodo, endpoint, **kwargs):
    """Executa uma requisição HTTP e trata erros da API."""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        resposta = requests.request(
            metodo,
            url,
            timeout=TIMEOUT_API,
            **kwargs,
        )

        if not resposta.ok:
            try:
                detalhe = resposta.json().get(
                    "detail",
                    "Erro ao processar a solicitação.",
                )
            except (ValueError, AttributeError):
                detalhe = "A API retornou uma resposta inválida."

            raise RuntimeError(
                f"Erro {resposta.status_code}: {detalhe}"
            )

        if resposta.status_code == 204:
            return None

        return resposta.json()

    except requests.RequestException as error:
        logger.exception("Falha na comunicação com a API.")
        raise RuntimeError(
            "Não foi possível conectar à API. "
            "Verifique se a FastAPI está em execução."
        ) from error


def exibir_analise(analise):
    """Exibe a análise estruturada devolvida pela API."""
    st.subheader("Resumo")
    st.write(analise.get("resumo", "Não disponível."))

    secoes = [
        ("Tópicos principais", analise.get("topicos_principais", [])),
        ("Decisões", analise.get("decisoes", [])),
        ("Dúvidas em aberto", analise.get("duvidas_em_aberto", [])),
    ]

    for titulo, itens in secoes:
        st.subheader(titulo)

        if itens:
            for item in itens:
                st.markdown(f"- {item}")
        else:
            st.caption("Nenhum item identificado.")

    st.subheader("Tarefas")
    tarefas = analise.get("tarefas", [])

    if tarefas:
        for tarefa in tarefas:
            st.markdown(f"- **Tarefa:** {tarefa['descricao']}")
            st.caption(
                f"Responsável: {tarefa.get('responsavel') or 'Não identificado'}"
            )
    else:
        st.caption("Nenhuma tarefa identificada.")


def executar_transcricao(arquivo):
    """Envia o arquivo à API e guarda o resultado na sessão."""
    try:
        with st.spinner("Enviando arquivo para transcrição..."):
            resultado = requisicao_api(
                "POST",
                "/transcricoes",
                files={
                    "file": (
                        arquivo.name,
                        arquivo.getvalue(),
                        arquivo.type or "application/octet-stream",
                    )
                },
            )

        transcricao = resultado.get("transcript_text", "")

        if not transcricao.strip():
            st.error("A API não retornou o texto da transcrição.")
            return

        st.session_state["transcricao_atual"] = transcricao
        st.session_state["nome_arquivo_transcricao"] = resultado.get(
            "filename", arquivo.name
        )
        st.session_state["transcricao_id"] = resultado["id"]
        st.session_state["analise_atual"] = None

        st.success("Transcrição concluída e salva!")

    except (RuntimeError, KeyError) as error:
        logger.exception("Falha na transcrição.")
        st.error(str(error))


def executar_analise():
    """Solicita a análise da transcrição já salva na API."""
    transcricao_id = st.session_state.get("transcricao_id")

    if transcricao_id is None:
        st.warning("Faça uma transcrição antes de solicitar a análise.")
        return

    try:
        with st.spinner("Analisando o conteúdo..."):
            resultado = requisicao_api(
                "POST",
                f"/transcricoes/{transcricao_id}/analise",
            )

        analise = resultado.get("result", resultado)
        st.session_state["analise_atual"] = analise
        st.success("Análise concluída!")

    except (RuntimeError, AttributeError) as error:
        logger.exception("Falha na análise.")
        st.error(str(error))


def inicializar_chat(arquivo_pdf):
    """Envia um PDF à API e cria uma sessão de chat."""
    try:
        with st.spinner("Enviando PDF e preparando o chat..."):
            resultado = requisicao_api(
                "POST",
                "/chat-pdf/sessoes",
                files={
                    "file": (
                        arquivo_pdf.name,
                        arquivo_pdf.getvalue(),
                        "application/pdf",
                    )
                },
            )

        st.session_state["pdf_sessao_id"] = resultado["sessao_id"]
        st.session_state["pdf_historico"] = []
        st.success("Chat com PDF inicializado!")

    except (RuntimeError, KeyError) as error:
        logger.exception("Falha ao inicializar o chat PDF.")
        st.error(str(error))


def perguntar_pdf(pergunta):
    """Envia uma pergunta à sessão de chat criada pela API."""
    sessao_id = st.session_state.get("pdf_sessao_id")

    if not sessao_id:
        st.warning("Envie um PDF e inicialize o chat primeiro.")
        return

    try:
        resultado = requisicao_api(
            "POST",
            f"/chat-pdf/sessoes/{sessao_id}/perguntas",
            json={"pergunta": pergunta},
        )

        st.session_state["pdf_historico"].append(
            {
                "pergunta": pergunta,
                "resposta": resultado.get("resposta", ""),
                "fontes": resultado.get("fontes", []),
            }
        )

    except RuntimeError as error:
        logger.exception("Falha ao consultar o PDF.")
        st.error(str(error))


def pagina_transcricao():
    st.subheader("Transcreva e analise áudios e vídeos")

    tab_video, tab_audio = st.tabs(["Vídeo", "Áudio"])

    with tab_video:
        arquivo_video = st.file_uploader(
            "Adicione um vídeo",
            type=["mp4", "mov"],
            key="video_file",
        )

        if arquivo_video and st.button("Transcrever vídeo"):
            executar_transcricao(arquivo_video)

    with tab_audio:
        arquivo_audio = st.file_uploader(
            "Adicione um áudio",
            type=["mp3", "m4a"],
            key="audio_file",
        )

        if arquivo_audio and st.button("Transcrever áudio"):
            executar_transcricao(arquivo_audio)

    transcricao = st.session_state.get("transcricao_atual")

    if transcricao:
        st.divider()
        st.subheader(
            f"Transcrição: "
            f"{st.session_state.get('nome_arquivo_transcricao', 'Arquivo')}"
        )

        st.text_area(
            "Texto transcrito",
            value=transcricao,
            height=250,
            disabled=True,
        )

        if st.button("Analisar transcrição"):
            executar_analise()

        analise = st.session_state.get("analise_atual")

        if analise:
            exibir_analise(analise)


def pagina_chat_pdf():
    st.subheader("Converse com seus documentos")

    arquivo_pdf = st.file_uploader(
        "Adicione um arquivo PDF",
        type=["pdf"],
        key="pdf_upload",
    )

    if arquivo_pdf and st.button("Inicializar chat"):
        inicializar_chat(arquivo_pdf)

    if st.session_state.get("pdf_sessao_id"):
        st.caption("Sessão de chat ativa.")

    for item in st.session_state.get("pdf_historico", []):
        with st.chat_message("user"):
            st.write(item["pergunta"])

        with st.chat_message("assistant"):
            st.write(item["resposta"])

            if item["fontes"]:
                with st.expander("Consultar fontes"):
                    for fonte in item["fontes"]:
                        st.write(fonte.get("arquivo", "Documento"))
                        if fonte.get("pagina") is not None:
                            st.caption(
                                f"Página: {fonte['pagina'] + 1}"
                            )

    pergunta = st.chat_input("Faça uma pergunta sobre o PDF")

    if pergunta:
        perguntar_pdf(pergunta)
        st.rerun()


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