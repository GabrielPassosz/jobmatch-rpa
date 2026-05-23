import time
import webbrowser
from urllib.parse import quote_plus

from src.config_loader import (
    carregar_config,
)

from src.resume_analyzer import (
    extrair_texto_curriculo,
    extrair_skills,
)

# ==========================================
# GERAR LINKS DO LINKEDIN
# ==========================================

def gerar_links_busca(
    skills
):
    links = []

    # ==============================
    # COMBINAÇÕES INTELIGENTES
    # ==============================

    if (
        "python" in skills
        and "rpa" in skills
    ):

        links.append(
            gerar_link(
                "Python RPA"
            )
        )

    if "selenium" in skills:

        links.append(
            gerar_link(
                "Python Selenium"
            )
        )

    if (
        "excel" in skills
        or "openpyxl" in skills
    ):

        links.append(
            gerar_link(
                "Python Excel Automation"
            )
        )

    if (
        "fiscal" in skills
        or "sped" in skills
    ):

        links.append(
            gerar_link(
                "Automação Fiscal Python"
            )
        )

    if "streamlit" in skills:

        links.append(
            gerar_link(
                "Python Streamlit"
            )
        )

    if "sql" in skills:

        links.append(
            gerar_link(
                "Python SQL"
            )
        )

    # ==============================
    # FALLBACK
    # ==============================

    if not links:

        links = [
            gerar_link(
                "Python Developer"
            ),
            gerar_link(
                "RPA Developer"
            ),
            gerar_link(
                "Automation Analyst"
            ),
        ]

    return links


# ==========================================
# GERAR LINK
# ==========================================

def gerar_link(
    termo_busca
):
    query = quote_plus(
        termo_busca
    )

    return (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={query}"
        "&f_TPR=r604800"
    )


# ==========================================
# MAIN
# ==========================================

def main():

    config = carregar_config()

    print(
        "\n🎯 JOBMATCH RPA\n"
    )

    print(
        "Lendo currículo..."
    )

    texto_curriculo = (
        extrair_texto_curriculo(
            config["CURRICULO"]
        )
    )

    print(
        "Extraindo skills..."
    )

    skills = extrair_skills(
        texto_curriculo
    )

    print(
        f"\nSkills encontradas:"
    )

    for skill in skills:

        print(
            f"• {skill}"
        )

    print(
        "\nGerando buscas..."
    )

    links = gerar_links_busca(
        skills
    )

    print(
        "\nLinks gerados:\n"
    )

    for link in links:

        print(link)

    print(
        "\nAbrindo navegador..."
    )

    # ==============================
    # ABRIR LINKS
    # ==============================

    for link in links:

        webbrowser.open(
            link
        )

        time.sleep(1.5)

    print(
        "\n✅ Buscas abertas com sucesso."
    )

    print(
        "\nRevise as vagas manualmente "
        "e adicione as melhores na "
        "planilha entrada/vagas.xlsx"
    )


if __name__ == "__main__":
    main()