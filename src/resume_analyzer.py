from pathlib import Path
import re

from pypdf import PdfReader
from docx import Document


# ==========================================
# BASE DE SKILLS
# ==========================================

SKILLS_BASE = [
    "python",
    "rpa",
    "selenium",
    "pyautogui",
    "pywinauto",
    "pandas",
    "openpyxl",
    "excel",
    "sql",
    "streamlit",
    "plotly",
    "api",
    "rest",
    "json",
    "git",
    "github",
    "docker",
    "linux",
    "windows",
    "regex",
    "javascript",
    "html",
    "css",
    "power bi",
    "web scraping",
    "scraping",
    "automacao",
    "automação",
    "fiscal",
    "sped",
    "efd",
    "ecac",
    "dctfweb",
]


# ==========================================
# EXTRAIR TEXTO DO CURRÍCULO
# ==========================================

def extrair_texto_curriculo(
    caminho_curriculo
):
    caminho = Path(caminho_curriculo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Currículo não encontrado: {caminho}"
        )

    extensao = caminho.suffix.lower()

    # ==============================
    # TXT
    # ==============================

    if extensao == ".txt":

        return caminho.read_text(
            encoding="utf-8"
        )

    # ==============================
    # PDF
    # ==============================

    elif extensao == ".pdf":

        reader = PdfReader(
            str(caminho)
        )

        textos = []

        for pagina in reader.pages:

            texto = pagina.extract_text()

            if texto:
                textos.append(texto)

        return "\n".join(textos)

    # ==============================
    # DOCX
    # ==============================

    elif extensao == ".docx":

        documento = Document(
            str(caminho)
        )

        textos = []

        for paragrafo in documento.paragraphs:
            textos.append(
                paragrafo.text
            )

        return "\n".join(textos)

    else:

        raise ValueError(
            "Formato de currículo não suportado."
        )


# ==========================================
# NORMALIZAR TEXTO
# ==========================================

def normalizar_texto(texto):
    texto = texto.lower()

    texto = texto.replace(
        "ç",
        "c"
    )

    texto = re.sub(
        r"\\s+",
        " ",
        texto
    )

    return texto


# ==========================================
# EXTRAIR SKILLS
# ==========================================

def extrair_skills(
    texto_curriculo
):
    texto = normalizar_texto(
        texto_curriculo
    )

    skills_encontradas = []

    for skill in SKILLS_BASE:

        skill_normalizada = (
            normalizar_texto(skill)
        )

        if skill_normalizada in texto:

            skills_encontradas.append(
                skill
            )

    return sorted(
        set(skills_encontradas)
    )