# Revisão de Dependências — Transcript AI

## 1. Objetivo

Documentar as dependências do projeto, suas finalidades e as decisões tomadas durante a revisão estrutural, preservando as funcionalidades existentes.

## 2. Dependências mantidas

| Dependência | Finalidade |
|---|---|
| `openai` | Cliente para integração com a API da OpenAI e transcrição de áudio. |
| `python-dotenv` | Carregamento de variáveis de ambiente. |
| `streamlit` | Interface web da aplicação. |
| `pypdf` | Extração de conteúdo textual de PDFs. |
| `imageio-ffmpeg` | Disponibilização do executável FFmpeg utilizado no processamento de vídeo. |
| `langchain-community` | Integrações para carregamento de PDFs e armazenamento vetorial FAISS. |
| `langchain-openai` | Integração dos modelos de linguagem e embeddings da OpenAI com LangChain. |
| `langchain-classic` | Cadeias de conversação e memória utilizadas no chat com PDFs. |
| `langchain-text-splitters` | Divisão dos documentos em trechos menores. |
| `faiss-cpu` | Índice vetorial utilizado na recuperação de trechos relevantes. |
| `fastapi` | Implementação da API. |
| `uvicorn[standard]` | Servidor para executar a API. |
| `sqlalchemy` | Mapeamento objeto-relacional e acesso ao banco de dados. |
| `psycopg[binary]` | Driver de conexão com PostgreSQL. |
| `alembic` | Gerenciamento de migrações do banco de dados. |
| `python-multipart` | Suporte ao recebimento de arquivos enviados por formulários e endpoints. |
| `httpx` | Cliente HTTP utilizado por dependências do ecossistema LangChain; não foi identificado uso direto no código analisado. |
| `requests` | Requisições HTTP utilizadas pela aplicação. |

## 3. Dependências removidas

### `moviepy`

Foi removida de `requirements.txt` porque não foi encontrado uso direto nos arquivos de código pesquisados. O processamento de vídeo utiliza `imageio-ffmpeg` e `subprocess` para extrair o áudio.

### `pydub`

Foi removida de `requirements.txt` porque não foi encontrado uso direto nos arquivos de código pesquisados.

Essas decisões se referem às dependências declaradas diretamente pelo projeto. Os pacotes não foram desinstalados do ambiente virtual durante a revisão.

## 4. Organização do código

A revisão identificou responsabilidades separadas nos seguintes módulos:

- `services/transcription.py`: transcrição de áudio por meio da OpenAI.
- `services/media.py`: validação de arquivos e extração de áudio de vídeos.
- `services/analysis_service.py`: geração de análises estruturadas.
- `services/pdf_chat.py`: inicialização e consulta do chat com PDFs.
- `rag/loader.py`: carregamento de documentos PDF.
- `rag/splitter.py`: divisão dos documentos em trechos.
- `rag/vector_store.py`: criação do índice vetorial e geração de embeddings.
- `rag/retriever.py`: configuração da recuperação de trechos relevantes.

Não foi identificada duplicação significativa nesses arquivos que justificasse uma refatoração imediata.

## 5. Configuração do Docker

O arquivo `.dockerignore` foi revisado para excluir, entre outros itens:

- Repositório Git.
- Ambientes virtuais.
- Arquivos de segredos e variáveis locais.
- Cache Python e de ferramentas de teste.
- Arquivos temporários e mídias locais.
- Configurações locais do VS Code.
- Artefatos de build.

O arquivo mantém uma exceção para `.env.example`. Esse arquivo deve conter somente valores de exemplo, nunca segredos reais.

## 6. Validação realizada

O comando abaixo foi executado após as alterações em `requirements.txt`:

`python -m pip check`

Resultado:

`No broken requirements found.`

Isso confirma que não foram encontrados conflitos entre os pacotes instalados. Essa verificação, isoladamente, não garante que todas as funcionalidades estejam funcionando nem que todas as dependências declaradas sejam necessárias.
