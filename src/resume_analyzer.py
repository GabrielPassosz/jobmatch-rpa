from pathlib import Path
import re
from collections import Counter

from pypdf import PdfReader
from docx import Document


# ==========================================
# PALAVRAS IGNORADAS
# ==========================================

STOPWORDS = {
    "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "uma", "um", "uns", "umas",
    "que", "e", "ou", "ao", "aos", "as", "os", "o", "a",
    "se", "sua", "seu", "suas", "seus", "como", "mais",
    "menos", "muito", "muita", "muitos", "muitas", "sobre",
    "entre", "até", "apos", "após", "durante", "visando",
    "contribuem", "efetivamente", "rotina", "trabalho",
    "experiencia", "experiência", "conhecimento", "atuando",
    "area", "área", "atuação", "atual", "conclusao", "conclusão",
}


# ==========================================
# PADRÕES IMPORTANTES DO CURRÍCULO
# ==========================================

PADROES_CARGOS = [
    r"área de atuação:\s*([^\n\r]+)",
    r"area de atuacao:\s*([^\n\r]+)",
    r"cargo:\s*([^\n\r]+)",
    r"função:\s*([^\n\r]+)",
    r"funcao:\s*([^\n\r]+)",
]


PADROES_FORMACAO = [
    r"cursando\s+([^\n\r]+)",
    r"formação\s+([^\n\r]+)",
    r"formacao\s+([^\n\r]+)",
]


# ==========================================
# EXTRAIR TEXTO DO CURRÍCULO
# ==========================================

def extrair_texto_curriculo(caminho_curriculo):
    caminho = Path(caminho_curriculo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Currículo não encontrado: {caminho}"
        )

    extensao = caminho.suffix.lower()

    if extensao == ".txt":
        return caminho.read_text(encoding="utf-8", errors="ignore")

    if extensao == ".pdf":
        reader = PdfReader(str(caminho))
        textos = []

        for pagina in reader.pages:
            texto = pagina.extract_text()

            if texto:
                textos.append(texto)

        return "\n".join(textos)

    if extensao == ".docx":
        documento = Document(str(caminho))
        textos = []

        for paragrafo in documento.paragraphs:
            if paragrafo.text.strip():
                textos.append(paragrafo.text)

        return "\n".join(textos)

    raise ValueError(
        "Formato de currículo não suportado. Use .txt, .pdf ou .docx."
    )


# ==========================================
# NORMALIZAR TEXTO
# ==========================================

def normalizar_texto(texto):
    texto = texto.lower()

    substituicoes = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }

    for original, novo in substituicoes.items():
        texto = texto.replace(original, novo)

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


# ==========================================
# LIMPAR FRASE
# ==========================================

def limpar_frase(texto):
    texto = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s/-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


# ==========================================
# EXTRAIR CARGOS DO CURRÍCULO
# ==========================================

def extrair_cargos(texto_curriculo):
    cargos = []
    texto_original = texto_curriculo

    for padrao in PADROES_CARGOS:
        matches = re.findall(
            padrao,
            texto_original,
            flags=re.IGNORECASE
        )

        for match in matches:
            cargo = limpar_frase(match)

            if cargo and len(cargo) >= 3:
                cargos.append(cargo)

    return remover_duplicados(cargos)


# ==========================================
# EXTRAIR FORMAÇÕES
# ==========================================

def extrair_formacoes(texto_curriculo):
    formacoes = []

    for padrao in PADROES_FORMACAO:
        matches = re.findall(
            padrao,
            texto_curriculo,
            flags=re.IGNORECASE
        )

        for match in matches:
            formacao = limpar_frase(match)

            if formacao and len(formacao) >= 3:
                formacoes.append(formacao)

    return remover_duplicados(formacoes)


# ==========================================
# EXTRAIR PALAVRAS-CHAVE RELEVANTES
# ==========================================

def extrair_palavras_chave(texto_curriculo, limite=25):
    texto = normalizar_texto(texto_curriculo)

    palavras = re.findall(
        r"\b[a-zA-ZÀ-ÿ]{4,}\b",
        texto
    )

    palavras_filtradas = []

    for palavra in palavras:
        if palavra not in STOPWORDS:
            palavras_filtradas.append(palavra)

    contagem = Counter(palavras_filtradas)

    palavras_relevantes = [
        palavra
        for palavra, _ in contagem.most_common(limite)
    ]

    return palavras_relevantes


# ==========================================
# EXTRAIR FRASES RELEVANTES
# ==========================================

def extrair_frases_relevantes(texto_curriculo):
    linhas = texto_curriculo.splitlines()
    frases = []

    palavras_indicadoras = [
        "atendimento",
        "cadastro",
        "agendamento",
        "recepção",
        "recepcao",
        "paciente",
        "cliente",
        "consultório",
        "consultorio",
        "exames",
        "administrativo",
        "qualidade",
        "vendas",
        "crm",
        "excel",
        "whatsapp",
        "sistema",
        "hospital",
        "clínica",
        "clinica",
        "fonoaudiologia",
    ]

    for linha in linhas:
        linha_limpa = limpar_frase(linha)

        if len(linha_limpa) < 5:
            continue

        linha_normalizada = normalizar_texto(linha_limpa)

        for palavra in palavras_indicadoras:
            if normalizar_texto(palavra) in linha_normalizada:
                frases.append(linha_limpa)
                break

    return remover_duplicados(frases)


# ==========================================
# GERAR TERMOS DE BUSCA PELO CURRÍCULO
# ==========================================

def gerar_termos_busca_curriculo(texto_curriculo, limite=8):
    texto_normalizado = normalizar_texto(texto_curriculo)

    termos = []

    # Cargos explícitos do currículo
    cargos = extrair_cargos(texto_curriculo)
    termos.extend(cargos)

    # Regras por conteúdo real encontrado no currículo
    if "auxiliar administrativo" in texto_normalizado:
        termos.append("Auxiliar Administrativo")

    if "qualidade" in texto_normalizado:
        termos.append("Assistente de Qualidade")

    if "recepcao" in texto_normalizado or "recepção" in texto_curriculo.lower():
        termos.append("Recepcionista")

    if "paciente" in texto_normalizado or "hospital" in texto_normalizado:
        termos.append("Atendente Hospitalar")

    if "consultorio" in texto_normalizado or "consultório" in texto_curriculo.lower():
        termos.append("Auxiliar de Consultório")

    if "exames" in texto_normalizado:
        termos.append("Auxiliar de Exames")

    if "agendamento" in texto_normalizado or "consultas" in texto_normalizado:
        termos.append("Atendente de Agendamento")

    if "guias" in texto_normalizado:
        termos.append("Assistente Administrativo Clínica")

    if "crm" in texto_normalizado or "inside sales" in texto_normalizado:
        termos.append("Assistente Comercial")

    if "vendas" in texto_normalizado or "negociacao" in texto_normalizado:
        termos.append("Assistente de Vendas")

    if "excel" in texto_normalizado or "planilhas" in texto_normalizado:
        termos.append("Auxiliar Administrativo Excel")

    if "fonoaudiologia" in texto_normalizado:
        termos.append("Estágio Fonoaudiologia")

    termos = limpar_termos_busca(termos)

    if not termos:
        raise ValueError(
            "Nenhum termo relevante foi encontrado no currículo. "
            "Verifique se o caminho do currículo no config.ini está correto "
            "e se o texto do PDF está sendo extraído."
        )

    return termos[:limite]
# ==========================================
# COMPATIBILIDADE COM CÓDIGO ANTIGO
# ==========================================

def extrair_skills(texto_curriculo):
    return gerar_termos_busca_curriculo(texto_curriculo)


# ==========================================
# LIMPAR TERMOS
# ==========================================

def limpar_termos_busca(termos):
    termos_limpos = []

    for termo in termos:
        termo = limpar_frase(termo)

        if not termo:
            continue

        if len(termo) < 3:
            continue

        if len(termo.split()) > 6:
            termo = " ".join(termo.split()[:6])

        termos_limpos.append(termo)

    return remover_duplicados(termos_limpos)


# ==========================================
# REMOVER DUPLICADOS
# ==========================================

def remover_duplicados(lista):
    vistos = set()
    resultado = []

    for item in lista:
        chave = normalizar_texto(item)

        if chave not in vistos:
            vistos.add(chave)
            resultado.append(item)

    return resultado