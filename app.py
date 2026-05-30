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
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 JobMatch RPA")
st.caption("Buscador inteligente de vagas por currículo com IA")

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

        quantidade_por_termo = st.number_input(
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

    st.info(
        "Clique em **Buscar e analisar vagas** para a IA ler o currículo, "
        "gerar termos de busca, pesquisar no LinkedIn e montar o ranking."
    )

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

        st.success(
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