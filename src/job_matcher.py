import json
import pandas as pd

from google import genai
from google.genai import types


def carregar_vagas(caminho):
    return pd.read_excel(caminho)


def analisar_vagas(
    vagas,
    texto_curriculo,
    api_key,
    modelo,
    score_aplicar=70,
    score_avaliar=45,
):
    if vagas.empty:
        return []

    return analisar_vagas_em_lote_com_ia(
        vagas=vagas,
        texto_curriculo=texto_curriculo,
        api_key=api_key,
        modelo=modelo,
        score_aplicar=score_aplicar,
        score_avaliar=score_avaliar,
    )


def analisar_vagas_em_lote_com_ia(
    vagas,
    texto_curriculo,
    api_key,
    modelo,
    score_aplicar=70,
    score_avaliar=45,
):
    client = genai.Client(api_key=api_key)

    vagas_para_ia = []

    for index, vaga in vagas.reset_index(drop=True).iterrows():
        vagas_para_ia.append({
            "id": int(index),
            "cargo": str(vaga.get("Cargo", "")),
            "empresa": str(vaga.get("Empresa", "")),
            "localizacao": str(vaga.get("Localizacao", "")),
            "modelo": str(vaga.get("Modelo", "")),
            "senioridade": str(vaga.get("Senioridade", "")),
            "link": str(vaga.get("Link", "")),
            "descricao": limitar_texto(str(vaga.get("Descricao", "")), 1800),
        })

    prompt = f"""
Você é um especialista em recrutamento.

Compare o currículo abaixo com cada vaga da lista e retorne um ranking de compatibilidade.

Regras:
- Considere equivalências entre português e inglês.
- Considere experiência prática, ferramentas, área profissional, senioridade e atividades.
- Não faça comparação literal de palavras.
- Não marque como faltante uma skill equivalente já presente no currículo.
- Score deve ir de 0 a 100.
- Recomendação:
  - APLICAR se score >= {score_aplicar}
  - AVALIAR se score >= {score_avaliar}
  - BAIXA COMPATIBILIDADE se score abaixo disso.
- Retorne um resultado para cada vaga enviada.
- Use o mesmo id recebido em cada vaga.

CURRÍCULO:
{limitar_texto(texto_curriculo, 6000)}

VAGAS:
{json.dumps(vagas_para_ia, ensure_ascii=False)}
"""

    schema = {
        "type": "object",
        "properties": {
            "resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "score": {"type": "integer"},
                        "recomendacao": {"type": "string"},
                        "skills_encontradas": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "skills_faltantes": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "justificativa": {"type": "string"},
                    },
                    "required": [
                        "id",
                        "score",
                        "recomendacao",
                        "skills_encontradas",
                        "skills_faltantes",
                        "justificativa",
                    ],
                }
            }
        },
        "required": ["resultados"],
    }

    response = client.models.generate_content(
        model=modelo,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        ),
    )

    dados = json.loads(response.text)

    resultados_ia = dados.get("resultados", [])

    resultados = []

    vagas_reset = vagas.reset_index(drop=True)

    for item in resultados_ia:
        idx = int(item["id"])

        if idx < 0 or idx >= len(vagas_reset):
            continue

        vaga = vagas_reset.iloc[idx]

        resultados.append({
            "Cargo": str(vaga.get("Cargo", "")),
            "Empresa": str(vaga.get("Empresa", "")),
            "Localizacao": str(vaga.get("Localizacao", "")),
            "Modelo": str(vaga.get("Modelo", "")),
            "Senioridade": str(vaga.get("Senioridade", "")),
            "Link": str(vaga.get("Link", "")),
            "Score": int(item["score"]),
            "Recomendacao": item["recomendacao"],
            "Skills_Encontradas": ", ".join(item["skills_encontradas"]),
            "Skills_Faltantes": ", ".join(item["skills_faltantes"]),
            "Resumo": item["justificativa"],
        })

    return sorted(
        resultados,
        key=lambda item: item["Score"],
        reverse=True,
    )


def limitar_texto(texto, limite):
    texto = str(texto)

    if len(texto) <= limite:
        return texto

    return texto[:limite] + "..."