🚀 JobMatch AI

Uma aplicação desenvolvida em Python que utiliza Inteligência Artificial, Automação Web e Análise de Dados para transformar um currículo em um ranking inteligente de oportunidades profissionais.

O objetivo do projeto foi estudar a integração entre diferentes tecnologias e aplicar conceitos de automação e IA para resolver um problema real: encontrar vagas compatíveis com o perfil profissional de forma mais eficiente.

📸 Visão Geral

O JobMatch AI realiza automaticamente todo o fluxo abaixo:

Currículo
    ↓
Extração de Texto
    ↓
Análise com IA
    ↓
Geração de Termos de Busca
    ↓
Pesquisa de Vagas
    ↓
Coleta de Informações
    ↓
Análise de Compatibilidade
    ↓
Ranking de Vagas
    ↓
Dashboard + Relatório Excel
✨ Funcionalidades
📄 Análise de Currículo

O sistema aceita currículos nos formatos:

PDF
DOCX
TXT

Após a leitura do documento, a IA identifica:

Perfil profissional
Área de atuação
Nível de senioridade
Habilidades principais
Cargos compatíveis
Termos de busca relevantes
🤖 Inteligência Artificial

Utilizando o Google Gemini, o sistema:

Analisa o currículo
Identifica competências profissionais
Sugere cargos-alvo
Gera termos inteligentes de pesquisa
Avalia a compatibilidade entre currículo e vaga
🔎 Busca Inteligente de Vagas

Com base no perfil identificado:

Gera automaticamente pesquisas relevantes
Realiza buscas por localização
Permite pesquisar vagas em qualquer país, estado ou cidade

Exemplos:

Curitiba, Brasil
São Paulo, Brasil
Lisboa, Portugal
Madrid, Espanha
New York, USA
London, United Kingdom
🌐 Automação com Selenium

A aplicação utiliza Selenium para:

Navegar automaticamente pelo LinkedIn Jobs
Realizar pesquisas
Coletar vagas
Extrair descrições
Capturar informações relevantes

Incluindo o tratamento automático de modais de login.

📊 Ranking Inteligente

Cada vaga encontrada é analisada pela IA.

O sistema gera:

Score de compatibilidade
Skills encontradas
Skills faltantes
Justificativa da recomendação

Classificando as oportunidades como:

APLICAR
AVALIAR
BAIXA COMPATIBILIDADE
📈 Dashboard Interativo

Desenvolvido com Streamlit.

O dashboard permite:

Upload de currículo
Configuração dos filtros
Visualização dos resultados
Ranking das vagas
Gráficos de distribuição
Métricas de desempenho
📑 Relatórios Excel

O sistema gera automaticamente:

Ranking completo
Resumo executivo
Estatísticas gerais
Classificação das vagas
🛠️ Tecnologias Utilizadas
Backend
Python
Pandas
OpenPyXL
Inteligência Artificial
Google Gemini AI
Automação
Selenium
Interface
Streamlit
Visualização
Plotly
Processamento de Documentos
PyPDF
python-docx
📂 Estrutura do Projeto
jobmatch-ai/
│
├── app.py
├── main.py
├── config.ini
├── requirements.txt
│
├── entrada/
│   ├── curriculo.pdf
│   └── vagas.xlsx
│
├── logs/
│
├── saida/
│
└── src/
    ├── config_loader.py
    ├── resume_analyzer.py
    ├── gemini_resume_analyzer.py
    ├── linkedin_scraper.py
    ├── job_matcher.py
    ├── excel_report.py
    ├── save_jobs_excel.py
    └── logger_config.py
⚙️ Configuração
1. Clone o repositório
git clone https://github.com/seu-usuario/jobmatch-ai.git

cd jobmatch-ai
2. Crie o ambiente virtual
python -m venv venv

Windows:

venv\Scripts\activate

Linux/Mac:

source venv/bin/activate
3. Instale as dependências
pip install -r requirements.txt
4. Configure o arquivo config.ini
[GEMINI]
GEMINI_API_KEY = SUA_CHAVE
MODELO = gemini-2.5-flash
🚀 Executando o Projeto
Dashboard Streamlit
streamlit run app.py
Execução via terminal
python main.py
🎯 Objetivos de Aprendizado

Este projeto foi desenvolvido para aprofundar conhecimentos em:

Automação de Processos
Inteligência Artificial Generativa
Engenharia de Software
Web Scraping
Processamento de Documentos
Desenvolvimento de Dashboards
Integração entre APIs
Análise de Dados
🔮 Melhorias Futuras
 Integração com outras plataformas de vagas
 Histórico de execuções
 Dashboard avançado
 Ranking por empresa
 Recomendação de cursos
 Sugestões para melhoria do currículo
 Exportação para PDF
 Busca multi-idioma
📹 Demonstração

Em breve será disponibilizado um vídeo demonstrando:

Upload do currículo
Análise com IA
Busca automática de vagas
Ranking de compatibilidade
Geração de relatórios
👨‍💻 Autor

Gabriel Luiz Batista Passos

Desenvolvedor com foco em:

Python
Automação de Processos
Inteligência Artificial
RPA
Engenharia de Software

LinkedIn:
www.linkedin.com/in/gabriel-luiz-batista-passos

GitHub:
https://github.com/GabrielLuizBatistaPassos