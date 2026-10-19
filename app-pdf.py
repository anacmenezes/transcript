import  streamlit as st
import time
from backend import cria_chain_conversa, folder_files

def chat_app():
    st.header("Bem vindo ao ChatPDF", divider=True)
    if not "Chain" in st.session_state:
        st.error("Faça o upload de pdfs para começas")
        st.stop()

    chain = st.session_state["chain"]
    memory =  chain.memory
    mensagens =  memory.load_memory_variable({})["chat_history"]

    container = st.container()
    for mensagem in mensagens:
        chat = container.chat_message(mensagem.type)
        chat.markdown(mensagem.content)

    nova_mensagem = st.chat_input("Converse com seus documentos")
    if nova_mensagem:
        chat = container.chat_message("human")
        chat.markdown(nova_mensagem)
        chat = container.chat_message("ai")
        chat.markdown("Gerando Resposta")
        chain.invoke({"question" : nova_mensagem})
        st.rerun()

def save_uploaded_files(uploaded_files, folder):
    for file in folder.glob("*.pdf"):
        file.unlink()

    for file in uploaded_files:
        (folder / file.name).write_bytes(file.read())

def main():
    with st.sidebar:
        st.header("Upload de PDFs")
        uploaded_pdfs = st.file_uploader("Adicione arquivos PDF",
                                         type="pdf",
                                         accept_multiple_files=True)
        if uploaded_pdfs:
            save_uploaded_files(uploaded_pdfs, folder_files)
            st.success(f"{len(uploaded_pdfs)} arquivos(s) salvo(s) com sucesso!")
        
        lable_botao = "Inicializar Chat"
        if "chain" in st.session_state:
            lable_botao = "Atualizar Chat"
        if st.button(lable_botao, use_container_width=True):
            if len(list(folder_files.glob("*.pdf"))) == 0:
                st.error("Adicione arquivos pdf para inicializar o chat")
            else:
                st.success("Inicializando o Chat...")
                cria_chain_conversa()
                st.rerun()
    chat_app()

if __name__ == "__main__":
    main()