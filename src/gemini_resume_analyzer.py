import json

from google import genai
from google.genai import types


def analisar_curriculo_com_gemini(texto_curriculo, api_key, modelo):
    if not texto_curriculo or len(texto_curriculo.strip()) < 50:
        raise ValueError(
            "O texto extraído do currículo está vazio ou muito curto."
        )

    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        raise ValueError(
            "GEMINI_API_KEY não configurada no config.ini."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
Você é um especialista em recrutamento e análise de currículos.

Leia o currículo completo e identifique vagas compatíveis.

Regras:
- Não retorne palavras soltas.
- Não retorne características comportamentais isoladas.
- Não retorne nome de empresa, cidade, telefone, e-mail ou LinkedIn.
- Retorne termos reais que funcionem como pesquisa no LinkedIn Jobs.
- Os termos precisam ser cargos, áreas profissionais ou combinações pesquisáveis.
- O resultado deve funcionar para qualquer área profissional, não apenas tecnologia.

Currículo:
{texto_curriculo}
"""

    schema = {
        "type": "object",
        "properties": {
            "perfil_profissional": {"type": "string"},
            "area_principal": {"type": "string"},
            "nivel_estimado": {"type": "string"},
            "cargos_alvo": {
                "type": "array",
                "items": {"type": "string"},
            },
            "termos_busca_linkedin": {
                "type": "array",
                "items": {"type": "string"},
            },
            "skills_principais": {
                "type": "array",
                "items": {"type": "string"},
            },
            "justificativa": {"type": "string"},
        },
        "required": [
            "perfil_profissional",
            "area_principal",
            "nivel_estimado",
            "cargos_alvo",
            "termos_busca_linkedin",
            "skills_principais",
            "justificativa",
        ],
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

    if not dados.get("termos_busca_linkedin"):
        raise ValueError(
            "O Gemini não conseguiu gerar termos de busca compatíveis com o currículo."
        )

    return dados