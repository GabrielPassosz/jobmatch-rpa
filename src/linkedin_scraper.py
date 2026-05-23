import time
from urllib.parse import quote_plus

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


LINKEDIN_BASE_URL = (
    "https://www.linkedin.com/jobs/search"
    "?trk=guest_homepage-basic_guest_nav_menu_jobs"
    "&position=1"
    "&pageNum=0"
)


def iniciar_navegador(headless=False):
    options = Options()
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)

    return driver


def gerar_termos_busca_por_skills(skills):
    skills = [skill.lower() for skill in skills]

    termos = []

    if "python" in skills and "rpa" in skills:
        termos.append("Python RPA")

    if "python" in skills and "selenium" in skills:
        termos.append("Python Selenium")

    if "python" in skills and "excel" in skills:
        termos.append("Python Excel Automation")

    if "python" in skills and "sql" in skills:
        termos.append("Python SQL")

    if "streamlit" in skills:
        termos.append("Python Streamlit")

    if "fiscal" in skills or "sped" in skills or "efd" in skills:
        termos.append("Automação Fiscal Python")

    if not termos:
        termos = [
            "Python Developer",
            "RPA Developer",
            "Automation Analyst",
        ]

    return termos[:5]


def montar_url_busca(termo_busca):
    termo_formatado = quote_plus(termo_busca)

    return (
        f"{LINKEDIN_BASE_URL}"
        f"&keywords={termo_formatado}"
    )


def buscar_vagas_por_curriculo(
    skills_curriculo,
    quantidade_por_termo=5,
    headless=False,
):
    termos_busca = gerar_termos_busca_por_skills(
        skills_curriculo
    )

    print("\nTermos gerados com base no currículo:")

    for termo in termos_busca:
        print(f"• {termo}")

    driver = iniciar_navegador(
        headless=headless
    )

    vagas_coletadas = []

    try:
        for termo in termos_busca:
            print(f"\nBuscando vagas para: {termo}")

            url = montar_url_busca(
                termo
            )

            driver.get(url)

            time.sleep(5)

            vagas = coletar_vagas_pagina(
                driver=driver,
                termo_busca=termo,
                quantidade=quantidade_por_termo,
            )

            vagas_coletadas.extend(
                vagas
            )

    finally:
        driver.quit()

    df = pd.DataFrame(
        vagas_coletadas
    )

    if not df.empty:
        df = df.drop_duplicates(
            subset=["Cargo", "Empresa", "Link"]
        )

    return df


def coletar_vagas_pagina(
    driver,
    termo_busca,
    quantidade=5,
):
    vagas = []

    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "ul.jobs-search__results-list li"
    )

    if not cards:
        cards = driver.find_elements(
            By.CSS_SELECTOR,
            ".job-search-card"
        )

    print(f"Cards encontrados: {len(cards)}")

    for card in cards[:quantidade]:
        try:
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                card
            )

            time.sleep(1)

            cargo = extrair_texto_seguro(
                card,
                [
                    ".base-search-card__title",
                    "h3",
                ]
            )

            empresa = extrair_texto_seguro(
                card,
                [
                    ".base-search-card__subtitle",
                    "h4",
                ]
            )

            localizacao = extrair_texto_seguro(
                card,
                [
                    ".job-search-card__location",
                    ".job-search-card__location span",
                ]
            )

            link = extrair_link_vaga(
                card
            )

            descricao = coletar_descricao_vaga(
                driver,
                card
            )

            vagas.append({
                "Cargo": cargo,
                "Empresa": empresa,
                "Localizacao": localizacao,
                "Modelo": "Não informado",
                "Senioridade": "Não informado",
                "Link": link,
                "Descricao": descricao,
                "Termo_Busca": termo_busca,
            })

            print(f"Vaga coletada: {cargo} | {empresa}")

        except Exception as erro:
            print(f"Erro ao coletar card: {erro}")
            continue

    return vagas


def coletar_descricao_vaga(
    driver,
    card
):
    try:
        card.click()

        time.sleep(2)

        seletores_descricao = [
            ".show-more-less-html__markup",
            ".description__text",
            ".jobs-description-content__text",
        ]

        for seletor in seletores_descricao:
            elementos = driver.find_elements(
                By.CSS_SELECTOR,
                seletor
            )

            if elementos:
                texto = elementos[0].text.strip()

                if texto:
                    return texto

    except Exception:
        pass

    return "Descrição não coletada"


def extrair_texto_seguro(
    elemento_base,
    seletores
):
    for seletor in seletores:
        try:
            elemento = elemento_base.find_element(
                By.CSS_SELECTOR,
                seletor
            )

            texto = elemento.text.strip()

            if texto:
                return texto

        except Exception:
            continue

    return "Não informado"


def extrair_link_vaga(
    card
):
    try:
        link = card.find_element(
            By.CSS_SELECTOR,
            "a"
        )

        return link.get_attribute(
            "href"
        )

    except Exception:
        return ""


if __name__ == "__main__":
    skills_teste = [
        "python",
        "rpa",
        "selenium",
        "excel",
        "sql",
    ]

    vagas = buscar_vagas_por_curriculo(
        skills_curriculo=skills_teste,
        quantidade_por_termo=3,
        headless=False,
    )

    print(vagas)