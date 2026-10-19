<h1 align="center">🎙️ Transcript AI</h1>

<p align="center">
  <strong>Transcrição inteligente de áudios e vídeos com Python e OpenAI</strong>
</p>

<p align="center">
  <a href="#sobre-o-projeto">Sobre o projeto</a> •
  <a href="#tecnologias">Tecnologias</a> •
  <a href="#practices-adopted">Práticas adotadas</a> •
  <a href="#pre-requisites">Requisitos</a> •
  <a href="#how-to-installing">Instalando o projeto</a> •
  <a href="#how-to-use">Como executar</a> •
  <a href="#security">Segurança</a>
</p>

<p align="center">
  <a href="https://github.com/anacmenezes/transcript-ai">
    <img src="https://img.shields.io/badge/GitHub-Projeto-black?logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Status-Em%20desenvolvimento-orange" alt="Status: em desenvolvimento">
</p>

<h2 id="sobre-o-projeto">📌 Sobre o projeto</h2>

<p>
O <strong>Transcript AI</strong> é uma aplicação desenvolvida em Python para transcrever arquivos de áudio e vídeo por meio da API da OpenAI. A interface web, construída com Streamlit, permite enviar arquivos e visualizar o texto transcrito.
</p>

<p>
Para vídeos, a aplicação utiliza MoviePy para extrair o áudio antes de enviá-lo ao serviço de transcrição. O projeto está em evolução para uma plataforma de análise de conteúdo com recursos de IA generativa.
</p>

<h3>Funcionalidades implementadas</h3>

<ul>
  <li>Interface web com abas para áudio e vídeo</li>
  <li>Upload de arquivos MP3 e MP4</li>
  <li>Extração de áudio de vídeos com MoviePy</li>
  <li>Transcrição em português com o modelo Whisper da OpenAI</li>
  <li>Campo opcional de contexto (prompt) para auxiliar a transcrição</li>
  <li>Exibição da transcrição na interface</li>
</ul>

<h2 id="tecnologias">🔌 Tecnologias</h2>

<ul>
  <li><a href="https://www.python.org/">Python</a></li>
  <li><a href="https://platform.openai.com/docs/">OpenAI API</a></li>
  <li>Whisper (speech-to-text)</li>
  <li><a href="https://zulko.github.io/moviepy/">MoviePy</a> — extração de áudio de vídeos</li>
  <li><a href="https://streamlit.io/">Streamlit</a> — interface web e upload de arquivos</li>
  <li><a href="https://pypi.org/project/python-dotenv/">python-dotenv</a> — suporte ao carregamento de variáveis de ambiente (dependência declarada)</li>
</ul>

<h2 id="practices-adopted">📖 Práticas adotadas</h2>
<ul>
  <li>Integração com serviço externo de transcrição por API</li>
  <li>Separação inicial das funções de transcrição de áudio e vídeo</li>
  <li>Interface interativa para upload e visualização de resultados</li>
  <li>Uso de ambiente virtual Python</li>
  <li>Configuração de credenciais por variável de ambiente</li>
  <li>Desenvolvimento incremental com foco em evolução arquitetural</li>
</ul>

<h2 id="pre-requisites">💻 Requisitos</h2>
<p>Para executar a aplicação localmente, é necessário:</p>
<ul>
  <li>Python (ambiente atualmente testado com 3.13.14)</li>
  <li>Chave de API da OpenAI com acesso ao serviço de transcrição e faturamento configurado conforme necessário</li>
  <li>Dependências listadas em <code>requirements.txt</code></li>
  <li>FFmpeg disponível conforme a configuração de processamento de vídeo do ambiente</li>
</ul>

<h2 id="how-to-installing">🚀 Instalando o projeto</h2>

<p>Clone o repositório:</p>
<pre><code>git clone https://github.com/anacmenezes/transcript-ai.git</code></pre>

<p>Acesse a pasta:</p>
<pre><code>cd transcript-ai</code></pre>

<p>Crie um ambiente virtual:</p>
<pre><code>python -m venv .venv</code></pre>

<p>Ative o ambiente no PowerShell (Windows):</p>
<pre><code>.\.venv\Scripts\Activate.ps1</code></pre>

<p>Instale as dependências:</p>
<pre><code>python -m pip install -r requirements.txt</code></pre>

<p>Crie um arquivo <code>.env</code> na raiz do projeto e configure a variável:</p>
<pre><code>OPENAI_API_KEY=sua_chave_aqui</code></pre>

<p><strong>Nota:</strong> a versão atual do código utiliza <code>openai.Client()</code>, que lê <code>OPENAI_API_KEY</code> do ambiente. O carregamento automático do arquivo <code>.env</code> depende de como o ambiente de execução foi configurado; a integração explícita com <code>load_dotenv()</code> faz parte da próxima refatoração. Não publique a chave.</p>

<h2 id="how-to-use">▶️ Como executar</h2>

<p>Na pasta do projeto, inicie a interface:</p>
<pre><code>streamlit run app.py</code></pre>

<p>Na aplicação:</p>
<ol>
  <li>Escolha a aba <strong>Áudio</strong> ou <strong>Vídeo</strong>.</li>
  <li>Envie um arquivo MP3 ou MP4, conforme a aba.</li>
  <li>Opcionalmente, informe um contexto para a transcrição.</li>
  <li>Aguarde o processamento e visualize o texto gerado.</li>
</ol>

<h2 id="security">🔐 Segurança</h2>
<p>A chave da OpenAI deve ser fornecida por variável de ambiente e nunca incluída no código-fonte. O arquivo <code>.env</code>, o ambiente virtual e os arquivos temporários devem ser excluídos do versionamento por meio de <code>.gitignore</code>.</p>
<p>Evite enviar gravações com dados pessoais, informações confidenciais ou material de terceiros sem autorização. Arquivos de áudio e vídeo são enviados ao serviço externo de transcrição.</p>

<h2 id="deploy">☁️ Deploy</h2>
<p>O projeto está em desenvolvimento local. Docker e deploy em nuvem estão previstos; ainda não há URL pública de produção.</p>

<h2 id="author">👩‍💻 Ana Carulina Menezes</h2>
<p>Projeto desenvolvido como parte do portfólio em <strong>Engenharia de IA</strong>, com foco em Python, integração com modelos de IA, aplicações de GenAI e evolução para arquiteturas de produção.</p>