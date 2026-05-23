import pandas as pd
import plotly.express as px
import streamlit as st

from src.config_loader import (
    carregar_config,
)

from src.resume_analyzer import (
    extrair_texto_curriculo,
    extrair_skills,
)

from src.job_matcher import (
    carregar_vagas,
    analisar_vagas,
)

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="JobMatch RPA",
    page_icon="🎯",
    layout="wide",
)

# ==========================================
# TÍTULO
# ==========================================

st.title(
    "🎯 JobMatch RPA"
)

st.caption(
    "Buscador Inteligente de Vagas por Currículo"
)

# ==========================================
# CARREGAR CONFIG
# ==========================================

config = carregar_config()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header(
        "Configurações"
    )

    caminho_curriculo = st.text_input(
        "Currículo",
        config["CURRICULO"]
    )

    caminho_vagas = st.text_input(
        "Planilha de vagas",
        config["VAGAS"]
    )

    score_aplicar = st.slider(
        "Score mínimo para APLICAR",
        0,
        100,
        int(
            config["SCORE_APLICAR"]
        )
    )

    score_avaliar = st.slider(
        "Score mínimo para AVALIAR",
        0,
        100,
        int(
            config["SCORE_AVALIAR"]
        )
    )

    executar = st.button(
        "Analisar vagas",
        type="primary"
    )

# ==========================================
# EXECUTAR ANÁLISE
# ==========================================

if executar:

    # ==============================
    # CURRÍCULO
    # ==============================

    texto_curriculo = (
        extrair_texto_curriculo(
            caminho_curriculo
        )
    )

    skills_curriculo = (
        extrair_skills(
            texto_curriculo
        )
    )

    # ==============================
    # VAGAS
    # ==============================

    vagas = carregar_vagas(
        caminho_vagas
    )

    resultados = analisar_vagas(
        vagas=vagas,
        skills_curriculo=skills_curriculo,
        score_aplicar=score_aplicar,
        score_avaliar=score_avaliar,
    )

    df = pd.DataFrame(
        resultados
    )

    # ==================================
    # SKILLS
    # ==================================

    st.subheader(
        "Skills encontradas no currículo"
    )

    st.write(
        ", ".join(skills_curriculo)
    )

    # ==================================
    # MÉTRICAS
    # ==================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Vagas analisadas",
        len(df)
    )

    col2.metric(
        "Aplicar",
        len(
            df[
                df["Recomendacao"]
                == "APLICAR"
            ]
        )
    )

    col3.metric(
        "Avaliar",
        len(
            df[
                df["Recomendacao"]
                == "AVALIAR"
            ]
        )
    )

    col4.metric(
        "Maior Score",
        (
            f'{df["Score"].max()}%'
            if not df.empty
            else "0%"
        )
    )

    # ==================================
    # TABELA PRINCIPAL
    # ==================================

    st.subheader(
        "Ranking de vagas"
    )

    st.dataframe(
        df[
            [
                "Cargo",
                "Empresa",
                "Localizacao",
                "Modelo",
                "Senioridade",
                "Score",
                "Recomendacao",
                "Skills_Encontradas",
                "Skills_Faltantes",
                "Link",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    # ==================================
    # GRÁFICO RECOMENDAÇÕES
    # ==================================

    st.subheader(
        "Distribuição por recomendação"
    )

    grafico_recomendacao = (
        px.histogram(
            df,
            x="Recomendacao",
            color="Recomendacao",
            title="Quantidade de vagas por recomendação",
        )
    )

    st.plotly_chart(
        grafico_recomendacao,
        use_container_width=True,
    )

    # ==================================
    # TOP 10
    # ==================================

    st.subheader(
        "Top 10 melhores vagas"
    )

    top10 = (
        df.sort_values(
            "Score",
            ascending=False
        )
        .head(10)
    )

    grafico_top10 = (
        px.bar(
            top10,
            x="Score",
            y="Cargo",
            color="Recomendacao",
            orientation="h",
            title="Top vagas por score",
        )
    )

    st.plotly_chart(
        grafico_top10,
        use_container_width=True,
    )

else:

    st.info(
        "Clique em 'Analisar vagas' para iniciar."
    )