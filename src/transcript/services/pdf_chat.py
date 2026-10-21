
import logging
from pathlib import Path

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.transcript.core.config import get_settings
from src.transcript.core.exceptions import (
    ChatInitializationError,
    ChatQueryError,
    DocumentProcessingError,
)

logger = logging.getLogger(__name__)


def importar_documentos(pasta_pdfs: Path):
    """Carrega o conteúdo textual dos PDFs da pasta."""

    if not pasta_pdfs.is_dir():
        raise DocumentProcessingError(
            "A pasta de documentos não existe."
        )

    arquivos_pdf = sorted(pasta_pdfs.glob("*.pdf"))

    if not arquivos_pdf:
        raise DocumentProcessingError(
            "Nenhum arquivo PDF foi encontrado."
        )

    documentos = []

    for arquivo in arquivos_pdf:
        try:
            documentos.extend(PyPDFLoader(str(arquivo)).load())
        except Exception as error:
            logger.exception("Falha ao carregar PDF: %s", arquivo.name)
            raise DocumentProcessingError(
                f"Não foi possível ler o PDF '{arquivo.name}'. "
                "Verifique se o arquivo está íntegro e protegido "
                "adequadamente para leitura."
            ) from error

    if not any(doc.page_content.strip() for doc in documentos):
        raise DocumentProcessingError(
            "Os PDFs não contêm texto extraível."
        )

    return documentos


def dividir_documentos(documentos):
    """Divide os documentos em trechos menores."""

    try:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        trechos = splitter.split_documents(documentos)

        for indice, trecho in enumerate(trechos):
            origem = trecho.metadata.get("source", "")
            trecho.metadata["source"] = Path(origem).name
            trecho.metadata["doc_id"] = indice

        if not trechos:
            raise DocumentProcessingError(
                "Não foi possível criar trechos dos documentos."
            )

        return trechos

    except DocumentProcessingError:
        raise
    except Exception as error:
        logger.exception("Falha ao dividir os documentos em trechos.")
        raise DocumentProcessingError(
            "Não foi possível preparar o conteúdo dos PDFs."
        ) from error


def criar_vector_store(documentos):
    """Gera embeddings e cria o índice vetorial FAISS."""

    try:
        settings = get_settings()
        embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            max_retries=2,
            request_timeout=60,
        )

        return FAISS.from_documents(
            documents=documentos,
            embedding=embeddings,
        )

    except Exception as error:
        logger.exception("Falha ao criar o índice vetorial.")
        raise ChatInitializationError(
            "Não foi possível indexar os documentos. "
            "Verifique a conexão com o serviço de embeddings."
        ) from error


def criar_chain_conversa(pasta_pdfs: Path):
    """Cria a cadeia de perguntas e respostas sobre os PDFs."""

    try:
        documentos = importar_documentos(pasta_pdfs)
        trechos = dividir_documentos(documentos)
        vector_store = criar_vector_store(trechos)

        settings = get_settings()
        modelo = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key,
            temperature=0,
            max_retries=2,
            timeout=90.0,
        )

        memoria = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        retriever = vector_store.as_retriever(
            search_kwargs={"k": 4}
        )

        return ConversationalRetrievalChain.from_llm(
            llm=modelo,
            retriever=retriever,
            memory=memoria,
            return_source_documents=True,
            verbose=False,
        )

    except (
        DocumentProcessingError,
        ChatInitializationError,
    ):
        raise
    except Exception as error:
        logger.exception("Falha ao inicializar o chat PDF.")
        raise ChatInitializationError(
            "Não foi possível inicializar o chat com os documentos."
        ) from error


def consultar_documentos(chain, pergunta: str):
    """Executa uma pergunta no chat e devolve a resposta com as fontes."""

    if not isinstance(pergunta, str) or not pergunta.strip():
        raise ChatQueryError("Digite uma pergunta antes de consultar.")

    if chain is None:
        raise ChatQueryError(
            "O chat não foi inicializado. Carregue os PDFs primeiro."
        )

    try:
        resultado = chain.invoke({"question": pergunta})

        if not isinstance(resultado, dict) or not resultado.get("answer"):
            raise ChatQueryError(
                "O chat não retornou uma resposta válida."
            )

        return resultado

    except ChatQueryError:
        raise
    except Exception as error:
        logger.exception("Falha ao consultar os documentos.")
        raise ChatQueryError(
            "Não foi possível responder à pergunta. "
            "Tente novamente mais tarde."
        ) from error