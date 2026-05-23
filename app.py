from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config_loader import carregar_config
from src.resume_analyzer import extrair_texto_curriculo, extrair_skills
from src.linkedin_scraper import buscar_vagas_por_curriculo
from src.job_matcher import carregar_vagas, analisar_vagas
from src.save_jobs_excel import salvar_vagas_excel
from src.excel_report import salvar_relatorio_excel


st.set_page_config(
    page_title="JobMatch RPA",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 JobMatch RPA")
st.caption("Buscador inteligente de vagas por currículo")

try:
    config = carregar_config()

    with st.sidebar:
        st.header("Configurações")

        caminho_curriculo = st.text_input(
            "Currículo",
            config["CURRICULO"],
        )

        caminho_vagas = st.text_input(
            "Planilha de vagas",
            config["VAGAS"],
        )

        quantidade_por_termo = st.number_input(
            "Quantidade de vagas por termo",
            min_value=1,
            max_value=30,
            value=int(config["QUANTIDADE_VAGAS"]),
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

        buscar_linkedin = st.checkbox(
            "Buscar vagas reais no LinkedIn",
            value=True,
        )

        executar = st.button(
            "Buscar e analisar vagas",
            type="primary",
        )

    st.info(
        "Clique em **Buscar e analisar vagas** para ler o currículo, buscar vagas no LinkedIn e gerar o ranking."
    )

    if executar:
        with st.spinner("Lendo currículo..."):
            texto_curriculo = extrair_texto_curriculo(
                caminho_curriculo
            )

            skills_curriculo = extrair_skills(
                texto_curriculo
            )

        st.subheader("Skills encontradas no currículo")
        st.write(", ".join(skills_curriculo))

        if buscar_linkedin:
            with st.spinner("Buscando vagas reais no LinkedIn..."):
                vagas = buscar_vagas_por_curriculo(
                    skills_curriculo=skills_curriculo,
                    quantidade_por_termo=int(quantidade_por_termo),
                    headless=False,
                )

            if vagas.empty:
                st.warning(
                    "Nenhuma vaga foi coletada no LinkedIn. Tente novamente ou reduza filtros."
                )
                st.stop()

            salvar_vagas_excel(
                vagas=vagas,
                caminho_excel=caminho_vagas,
            )

            st.success(
                f"{len(vagas)} vagas coletadas e salvas em {caminho_vagas}"
            )

        else:
            with st.spinner("Lendo vagas da planilha local..."):
                vagas = carregar_vagas(
                    caminho_vagas
                )

        with st.spinner("Calculando compatibilidade..."):
            resultados = analisar_vagas(
                vagas=vagas,
                skills_curriculo=skills_curriculo,
                score_aplicar=score_aplicar,
                score_avaliar=score_avaliar,
            )

            df = pd.DataFrame(
                resultados
            )

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

        st.success(
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