from pathlib import Path
import pandas as pd

from src.resume_analyzer import (
    SKILLS_BASE,
    normalizar_texto,
)


# ==========================================
# COLUNAS OBRIGATÓRIAS
# ==========================================

COLUNAS_OBRIGATORIAS = [
    "Cargo",
    "Empresa",
    "Localizacao",
    "Modelo",
    "Senioridade",
    "Link",
    "Descricao",
]


# ==========================================
# CARREGAR VAGAS
# ==========================================

def carregar_vagas(
    caminho_vagas
):
    caminho = Path(caminho_vagas)

    if not caminho.exists():

        raise FileNotFoundError(
            f"Planilha de vagas não encontrada: {caminho}"
        )

    df = pd.read_excel(caminho)

    # ==============================
    # VALIDAR COLUNAS
    # ==============================

    colunas_faltando = [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS
        if coluna not in df.columns
    ]

    if colunas_faltando:

        raise ValueError(
            f"Colunas obrigatórias ausentes: {colunas_faltando}"
        )

    # Remove linhas vazias

    df = df.dropna(
        subset=[
            "Cargo",
            "Empresa",
            "Descricao",
        ]
    )

    return df


# ==========================================
# ANALISAR VAGAS
# ==========================================

def analisar_vagas(
    vagas,
    skills_curriculo,
    score_aplicar=70,
    score_avaliar=45,
):
    resultados = []

    for _, vaga in vagas.iterrows():

        # ==============================
        # TEXTO DA VAGA
        # ==============================

        texto_vaga = " ".join([
            str(vaga["Cargo"]),
            str(vaga["Descricao"]),
            str(vaga["Senioridade"]),
            str(vaga["Modelo"]),
        ])

        # ==============================
        # SKILLS DA VAGA
        # ==============================

        skills_vaga = (
            extrair_skills_da_vaga(
                texto_vaga
            )
        )

        # ==============================
        # COMPARAÇÃO
        # ==============================

        skills_encontradas = sorted(
            set(skills_curriculo)
            .intersection(
                set(skills_vaga)
            )
        )

        skills_faltantes = sorted(
            set(skills_vaga)
            .difference(
                set(skills_curriculo)
            )
        )

        # ==============================
        # SCORE
        # ==============================

        score = calcular_score(
            skills_encontradas,
            skills_vaga,
        )

        # ==============================
        # RECOMENDAÇÃO
        # ==============================

        if score >= score_aplicar:

            recomendacao = "APLICAR"

        elif score >= score_avaliar:

            recomendacao = "AVALIAR"

        else:

            recomendacao = (
                "BAIXA COMPATIBILIDADE"
            )

        # ==============================
        # RESUMO
        # ==============================

        resumo = gerar_resumo(
            score,
            skills_encontradas,
            skills_faltantes,
        )

        # ==============================
        # RESULTADO FINAL
        # ==============================

        resultado = {
            "Cargo": vaga["Cargo"],
            "Empresa": vaga["Empresa"],
            "Localizacao": vaga["Localizacao"],
            "Modelo": vaga["Modelo"],
            "Senioridade": vaga["Senioridade"],
            "Link": vaga["Link"],
            "Score": score,
            "Recomendacao": recomendacao,
            "Skills_Encontradas": ", ".join(
                skills_encontradas
            ),
            "Skills_Faltantes": ", ".join(
                skills_faltantes
            ),
            "Resumo": resumo,
        }

        resultados.append(
            resultado
        )

    # ==============================
    # ORDENAR POR SCORE
    # ==============================

    resultados = sorted(
        resultados,
        key=lambda item: item["Score"],
        reverse=True,
    )

    return resultados


# ==========================================
# EXTRAIR SKILLS DA VAGA
# ==========================================

def extrair_skills_da_vaga(
    texto_vaga
):
    texto = normalizar_texto(
        texto_vaga
    )

    skills = []

    for skill in SKILLS_BASE:

        skill_normalizada = (
            normalizar_texto(skill)
        )

        if skill_normalizada in texto:

            skills.append(skill)

    return sorted(
        set(skills)
    )


# ==========================================
# CALCULAR SCORE
# ==========================================

def calcular_score(
    skills_encontradas,
    skills_vaga,
):
    if not skills_vaga:
        return 0

    score = (
        len(skills_encontradas)
        / len(skills_vaga)
    ) * 100

    return round(score)


# ==========================================
# GERAR RESUMO
# ==========================================

def gerar_resumo(
    score,
    skills_encontradas,
    skills_faltantes,
):
    if score >= 70:

        return (
            "Alta compatibilidade "
            "com o currículo."
        )

    elif score >= 45:

        return (
            "Compatibilidade média. "
            "Vale revisar a vaga."
        )

    elif skills_faltantes:

        return (
            "Baixa compatibilidade. "
            "Muitas skills importantes "
            "não foram encontradas."
        )

    return (
        "Vaga com poucas "
        "informações técnicas."
    )