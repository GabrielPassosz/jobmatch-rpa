from datetime import datetime
from pathlib import Path
import tempfile

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config_loader import carregar_config
from src.resume_analyzer import extrair_texto_curriculo
from src.gemini_resume_analyzer import analisar_curriculo_com_gemini
from src.linkedin_scraper import buscar_vagas_por_curriculo
from src.job_matcher import analisar_vagas
from src.save_jobs_excel import salvar_vagas_excel
from src.excel_report import salvar_relatorio_excel


st.set_page_config(
    page_title="JobMatch RPA",
    page_icon="",
    layout="wide",
)

st.markdown("""
<style>
:root {
    --bg: #07111F;
    --surface: #0F172A;
    --surface-soft: #1E293B;
    --border: rgba(255,255,255,0.08);

    --text: #F8FAFC;
    --muted: #94A3B8;

    --brand: #2563EB;
    --brand-2: #3B82F6;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.18), transparent 30%),
        radial-gradient(circle at top right, rgba(59,130,246,0.12), transparent 25%),
        var(--bg);
}
header[data-testid="stHeader"] {
    background: transparent;
}

div[data-testid="stToolbar"] {
    display: none;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

.block-container {
    max-width: 1180px;
    padding-top: 32px;
    padding-left: 36px;
    padding-right: 36px;
}

section[data-testid="stSidebar"] {
    background: rgba(18,18,20,0.96);
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p {
    color: var(--text) !important;
}

section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="input"] {
    background: var(--surface-soft) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--surface-soft);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 14px;
}

.hero-card {
    padding: 72px 56px;
    border-radius: 32px;
    background:
    linear-gradient(
        135deg,
        rgba(37,99,235,0.22),
        rgba(59,130,246,0.08)
    ),
    rgba(15,23,42,0.96);
    border: 1px solid var(--border);
    box-shadow: 0 30px 90px rgba(0,0,0,0.35);
    margin-bottom: 28px;
}

.hero-card h1 {
    max-width: 760px;
    margin: 0 0 22px 0;
    font-size: 64px;
    line-height: 1.02;
    letter-spacing: -0.06em;
    color: var(--text);
}

.hero-card p {
    max-width: 640px;
    margin: 0 0 34px 0;
    font-size: 20px;
    line-height: 1.65;
    color: var(--muted);
}

.hero-actions {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
}

.primary-pill,
.secondary-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 46px;
    padding: 0 22px;
    border-radius: 999px;
    font-weight: 700;
}

.primary-pill {
    background: linear-gradient(135deg, var(--brand), var(--brand-2));
    color: white;
}

.secondary-pill {
    color: white;
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.04);
}

.section-card {
    background: rgba(18,18,20,0.88);
    border: 1px solid var(--border);
    border-radius: 28px;
    padding: 34px;
    margin-bottom: 26px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.22);
}

.section-card h3 {
    color: var(--text);
    font-size: 28px;
    margin: 0 0 20px 0;
    letter-spacing: -0.03em;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.feature-card {
    background: var(--surface-soft);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 22px;
}

.feature-card h4 {
    color: var(--text);
    margin: 0 0 10px 0;
    font-size: 18px;
}

.feature-card p {
    color: var(--muted);
    margin: 0;
    line-height: 1.6;
    font-size: 15px;
}

.stButton > button {
    width: 100%;
    height: 50px;
    border-radius: 999px !important;
    background: linear-gradient(135deg, var(--brand), var(--brand-2)) !important;
    color: white !important;
    border: 1px solid transparent !important;
    font-weight: 800;
    transition: all .25s ease;
}

.stButton > button:hover {
    background: transparent !important;
    border-color: var(--brand) !important;
    color: white !important;
    box-shadow: 0 0 0 4px rgba(168,85,247,0.14);
    transform: translateY(-1px);
}

div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 18px;
    color: var(--text);
}

.stDataFrame,
div[data-testid="stDataFrame"] {
    border-radius: 22px;
    overflow: hidden;
    border: 1px solid var(--border);
}

div[data-testid="metric-container"] {
    background: #0F172A;
    border: 1px solid rgba(59,130,246,0.15);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.20);
}

div[data-testid="metric-container"] label {
    color: #94A3B8 !important;
}

div[data-testid="metric-container"] div {
    color: white !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid rgba(59,130,246,0.12);
}

@media (max-width: 900px) {
    .hero-card {
        padding: 48px 30px;
    }

    .hero-card h1 {
        font-size: 42px;
    }

    .feature-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero-card">
    <h1>Encontre vagas que combinam com o seu perfil.</h1>
    <p>
        O JobMatch RPA usa inteligência artificial para analisar seu currículo,
        buscar oportunidades no LinkedIn e montar um ranking com as melhores vagas.
    </p>
    <div class="hero-actions">
        <span class="primary-pill">Analisar currículo</span>
        <span class="secondary-pill">Buscar oportunidades</span>
    </div>
</div>
""", unsafe_allow_html=True)


try:
    config = carregar_config()

    with st.sidebar:
        st.header("Configurações")

        arquivo_curriculo = st.file_uploader(
            "Anexe seu currículo",
            type=["pdf", "docx", "txt"],
        )

        caminho_vagas = st.text_input(
            "Planilha de vagas",
            config["VAGAS"],
        )

        quantidade_por_termo = st.slider(
            "Quantidade de vagas por termo",
            min_value=1,
            max_value=30,
            value=int(config["QUANTIDADE_VAGAS"]),
        )

        localizacao = st.text_input(
            "Localização da busca",
            value="Brasil",
            help="Digite cidade, estado ou país. Ex: Curitiba, Brasil | New York, USA | Lisboa, Portugal",
        )

        score_aplicar = st.slider(
            "Score mínimo para APLICAR",
            0,
            100,
            int(config["SCORE_APLICAR"]),
        )

        score_avaliar = st.slider(
            "Score mínimo para AVALIAR",
            0,
            100,
            int(config["SCORE_AVALIAR"]),
        )

        executar = st.button(
            "Buscar e analisar vagas",
            type="primary",
        )

    st.markdown("## Como funciona")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.container(border=True)

        st.markdown("""
    ### 📄 Currículo

    Anexe seu currículo em PDF, DOCX ou TXT.

    A IA identifica:

    - Perfil profissional
    - Área de atuação
    - Senioridade
    - Cargos-alvo
    """)

    with col2:
        st.container(border=True)

        st.markdown("""
    ### 🔍 Busca Inteligente

    Escolha qualquer localização do mundo.

    O sistema pesquisa:

    - LinkedIn
    - Vagas compatíveis
    - Múltiplos termos
    - Diversas regiões
    """)

    with col3:
        st.container(border=True)

        st.markdown("""
    ### 🤖 Ranking IA

    As vagas são avaliadas automaticamente.

    Você recebe:

    - Score de aderência
    - Recomendações
    - Ranking
    - Relatório Excel
    """)

    if executar:
        if arquivo_curriculo is None:
            st.warning("Anexe um currículo antes de iniciar.")
            st.stop()

        sufixo = Path(arquivo_curriculo.name).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=sufixo,
        ) as arquivo_temporario:
            arquivo_temporario.write(
                arquivo_curriculo.getbuffer()
            )

            caminho_curriculo = arquivo_temporario.name

        with st.spinner("Lendo currículo..."):
            texto_curriculo = extrair_texto_curriculo(
                caminho_curriculo
            )

        with st.expander("Texto extraído do currículo"):
            st.text(texto_curriculo[:5000])

        with st.spinner("Analisando currículo com IA..."):
            dados_ia = analisar_curriculo_com_gemini(
                texto_curriculo=texto_curriculo,
                api_key=config["GEMINI_API_KEY"],
                modelo=config["MODELO_GEMINI"],
            )

        st.success("Currículo analisado com IA.")

        st.subheader("Perfil identificado pela IA")
        st.write(dados_ia["perfil_profissional"])

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Área principal:**")
            st.write(dados_ia["area_principal"])

        with col_b:
            st.markdown("**Nível estimado:**")
            st.write(dados_ia["nivel_estimado"])

        st.subheader("Cargos-alvo")
        st.write(", ".join(dados_ia["cargos_alvo"]))

        st.subheader("Termos de busca para LinkedIn")
        st.write(", ".join(dados_ia["termos_busca_linkedin"]))

        st.subheader("Skills principais")
        st.write(", ".join(dados_ia["skills_principais"]))

        with st.expander("Justificativa da IA"):
            st.write(dados_ia["justificativa"])

        termos_busca = dados_ia["termos_busca_linkedin"]

        with st.spinner("Buscando vagas reais no LinkedIn..."):
            vagas = buscar_vagas_por_curriculo(
                skills_curriculo=termos_busca,
                quantidade_por_termo=int(quantidade_por_termo),
                headless=False,
                localizacao=localizacao,
            )

        if vagas.empty:
            st.warning(
                "Nenhuma vaga foi coletada no LinkedIn. "
                "Tente novamente ou reduza a quantidade por termo."
            )
            st.stop()

        salvar_vagas_excel(
            vagas=vagas,
            caminho_excel=caminho_vagas,
        )

        st.info(
            f"{len(vagas)} vagas coletadas e salvas em {caminho_vagas}"
        )

        with st.spinner("Calculando compatibilidade das vagas..."):
            resultados = analisar_vagas(
                vagas=vagas,
                texto_curriculo=texto_curriculo,
                api_key=config["GEMINI_API_KEY"],
                modelo=config["MODELO_GEMINI"],
                score_aplicar=score_aplicar,
                score_avaliar=score_avaliar,
            )

            df = pd.DataFrame(resultados)

        data_execucao = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        pasta_saida = (
            Path(config["PASTA_SAIDA"])
            / data_execucao
        )

        pasta_saida.mkdir(
            parents=True,
            exist_ok=True,
        )

        caminho_relatorio = salvar_relatorio_excel(
            resultados=resultados,
            pasta_saida=pasta_saida,
        )

        st.info(
            f"Relatório Excel gerado: {caminho_relatorio}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Vagas analisadas",
            len(df),
        )

        col2.metric(
            "Aplicar",
            len(df[df["Recomendacao"] == "APLICAR"]),
        )

        col3.metric(
            "Avaliar",
            len(df[df["Recomendacao"] == "AVALIAR"]),
        )

        col4.metric(
            "Maior Score",
            f'{df["Score"].max()}%' if not df.empty else "0%",
        )

        st.subheader("Ranking de vagas")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Distribuição por recomendação")

        grafico_recomendacao = px.histogram(
            df,
            x="Recomendacao",
            color="Recomendacao",
            title="Quantidade de vagas por recomendação",
        )

        st.plotly_chart(
            grafico_recomendacao,
            use_container_width=True,
        )

        st.subheader("Top 10 melhores vagas")

        top10 = (
            df.sort_values(
                "Score",
                ascending=False,
            )
            .head(10)
        )

        grafico_top10 = px.bar(
            top10,
            x="Score",
            y="Cargo",
            color="Recomendacao",
            orientation="h",
            title="Top vagas por score",
        )

        st.plotly_chart(
            grafico_top10,
            use_container_width=True,
        )

except Exception as erro:
    st.error("Erro ao executar o JobMatch RPA.")
    st.exception(erro)