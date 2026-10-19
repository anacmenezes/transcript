
from pathlib import Path

from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.transcript.core.config import get_settings

def importar_documentos(pasta_pdfs: Path):
    documentos = []

    arquivos_pdf = sorted(pasta_pdfs.glob("*.pdf"))

    if not arquivos_pdf:
        raise ValueError("Nenhum arquivo PDF encontrado.")

    for arquivo in arquivos_pdf:
        loader = PyPDFLoader(str(arquivo))
        documentos.extend(loader.load())

    if not any(documento.page_content.strip() for documento in documentos):
        raise ValueError("Os PDFs não contêm texto extraível.")

    return documentos

def dividir_documentos(documentos):
    """Divide os documentos em trechos menores."""
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

    return trechos

def criar_vector_store(documentos):
    """Cria o índice vetorial dos documentos."""
    settings = get_settings()
    embeddings = OpenAIEmbeddings(
    api_key=settings.openai_api_key
)

    return FAISS.from_documents(
        documents=documentos,
        embedding=embeddings,
    )

def criar_chain_conversa(pasta_pdfs: Path):
    """Cria a cadeia de perguntas e respostas sobre os PDFs."""
    documentos = importar_documentos(pasta_pdfs)
    trechos = dividir_documentos(documentos)
    vector_store = criar_vector_store(trechos)

    modelo = ChatOpenAI(model="gpt-4o-mini")

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