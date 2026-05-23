from pathlib import Path
import re
import unicodedata
from collections import Counter

from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer


STOPWORDS = {
    "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "uma", "um", "uns", "umas",
    "que", "e", "ou", "ao", "aos", "as", "os", "o", "a",
    "se", "sua", "seu", "suas", "seus", "como", "mais", "menos",
    "muito", "muita", "muitos", "muitas", "sobre", "entre",
    "apos", "após", "durante", "visando", "rotina", "trabalho",
    "experiencia", "experiência", "conhecimento", "atuando",
    "profissional", "resumo", "educacao", "educação", "habilidades",
    "experiencias", "experiências", "brasil", "curitiba", "parana",
    "email", "telefone", "linkedin", "github", "contato",
}


def extrair_texto_curriculo(caminho_curriculo):
    caminho = Path(caminho_curriculo)

    if not caminho.exists():
        raise FileNotFoundError(f"Currículo não encontrado: {caminho}")

    extensao = caminho.suffix.lower()

    if extensao == ".txt":
        texto = caminho.read_text(encoding="utf-8", errors="ignore")
        return corrigir_texto_espacado(texto)

    if extensao == ".pdf":
        reader = PdfReader(str(caminho))
        textos = []

        for pagina in reader.pages:
            texto = pagina.extract_text()
            if texto:
                textos.append(texto)

        texto_final = "\n".join(textos)
        return corrigir_texto_espacado(texto_final)

    if extensao == ".docx":
        documento = Document(str(caminho))
        texto = "\n".join(
            p.text for p in documento.paragraphs if p.text.strip()
        )
        return corrigir_texto_espacado(texto)

    raise ValueError("Formato não suportado. Use .txt, .pdf ou .docx.")


def corrigir_texto_espacado(texto):
    linhas_corrigidas = []

    for linha in texto.splitlines():
        letras = re.findall(r"[A-Za-zÀ-ÿ]", linha)
        palavras_normais = re.findall(r"[A-Za-zÀ-ÿ]{2,}", linha)

        if len(letras) >= 6 and len(palavras_normais) <= 1:
            linha = re.sub(r"(?<=\w)\s(?=\w)", "", linha)

        linhas_corrigidas.append(linha)

    return "\n".join(linhas_corrigidas)


def normalizar_texto(texto):
    texto = corrigir_texto_espacado(texto)
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = re.sub(r"[^a-zA-Z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def limpar_linha(linha):
    linha = corrigir_texto_espacado(linha)
    linha = re.sub(r"\s+", " ", linha)
    return linha.strip()


def remover_dados_pessoais(texto):
    texto = re.sub(r"\S+@\S+", " ", texto)
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"www\.\S+", " ", texto)
    texto = re.sub(r"\+?\d[\d\s().-]{7,}", " ", texto)
    texto = re.sub(r"\b\d{5,}\b", " ", texto)
    return texto


def dividir_curriculo_em_linhas_profissionais(texto):
    texto = remover_dados_pessoais(texto)
    linhas = []

    for linha in texto.splitlines():
        linha = limpar_linha(linha)

        if len(linha) < 4:
            continue

        if parece_dado_pessoal(linha):
            continue

        linhas.append(linha)

    return linhas


def parece_dado_pessoal(linha):
    linha_normalizada = normalizar_texto(linha)

    if "linkedin" in linha_normalizada:
        return True

    if "gmail" in linha_normalizada or "hotmail" in linha_normalizada:
        return True

    if re.search(r"\d{5,}", linha_normalizada):
        return True

    return False


def extrair_frases_profissionais(texto):
    linhas = dividir_curriculo_em_linhas_profissionais(texto)

    frases = []

    palavras_excluir = {
        "resumo", "experiencia", "experiencias", "educacao",
        "formacao", "habilidades", "voluntariado", "idiomas"
    }

    for linha in linhas:
        normalizada = normalizar_texto(linha)

        if normalizada in palavras_excluir:
            continue

        qtd_palavras = len(normalizada.split())

        if 1 <= qtd_palavras <= 8:
            frases.append(linha)

    return remover_duplicados(frases)


def extrair_termos_tfidf(texto, limite=30):
    frases = extrair_frases_profissionais(texto)

    if not frases:
        raise ValueError(
            "Nenhuma frase profissional foi encontrada no currículo."
        )

    corpus = [
        normalizar_texto(frase)
        for frase in frases
        if len(normalizar_texto(frase)) >= 4
    ]

    if not corpus:
        raise ValueError(
            "O currículo foi lido, mas não há conteúdo profissional suficiente."
        )

    vectorizer = TfidfVectorizer(
        stop_words=list(STOPWORDS),
        ngram_range=(1, 3),
        max_features=100,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z]+\b",
    )

    try:
        matriz = vectorizer.fit_transform(corpus)
    except ValueError:
        return extrair_termos_por_frequencia(texto, limite)

    features = vectorizer.get_feature_names_out()
    scores = matriz.sum(axis=0).A1

    ranking = sorted(
        zip(features, scores),
        key=lambda item: item[1],
        reverse=True,
    )

    termos = []

    for termo, _ in ranking:
        termo = limpar_termo(termo)

        if termo_valido(termo):
            termos.append(termo)

    return remover_duplicados(termos)[:limite]


def extrair_termos_por_frequencia(texto, limite=30):
    texto = normalizar_texto(remover_dados_pessoais(texto))

    palavras = re.findall(r"\b[a-zA-Z]{3,}\b", texto)

    palavras = [
        palavra
        for palavra in palavras
        if palavra not in STOPWORDS
    ]

    if not palavras:
        raise ValueError(
            "Nenhuma palavra relevante foi encontrada no currículo."
        )

    contagem = Counter(palavras)

    return [
        palavra
        for palavra, _
        in contagem.most_common(limite)
        if termo_valido(palavra)
    ]


def gerar_termos_busca_curriculo(texto_curriculo, limite=8):
    if not texto_curriculo or len(texto_curriculo.strip()) < 50:
        raise ValueError(
            "O texto extraído do currículo está vazio ou muito curto."
        )

    frases = extrair_frases_profissionais(texto_curriculo)
    termos_tfidf = extrair_termos_tfidf(texto_curriculo, limite=40)

    termos = []

    # Prioriza frases curtas do currículo que parecem cargo/área/formação
    for frase in frases:
        frase_limpa = limpar_termo(frase)

        if 1 <= len(frase_limpa.split()) <= 5 and termo_valido(frase_limpa):
            termos.append(frase_limpa)

    # Depois adiciona termos extraídos por NLP
    for termo in termos_tfidf:
        if 1 <= len(termo.split()) <= 4:
            termos.append(termo)

    termos = limpar_lista_termos(termos)

    if not termos:
        raise ValueError(
            "Nenhum termo relevante foi encontrado no currículo. "
            "Verifique se o PDF está sendo lido corretamente."
        )

    return termos[:limite]


def extrair_skills(texto_curriculo):
    return gerar_termos_busca_curriculo(texto_curriculo)


def limpar_termo(termo):
    termo = corrigir_texto_espacado(termo)
    termo = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s/-]", " ", termo)
    termo = re.sub(r"\s+", " ", termo)
    return termo.strip()


def termo_valido(termo):
    termo_normalizado = normalizar_texto(termo)

    if len(termo_normalizado) < 3:
        return False

    if termo_normalizado in STOPWORDS:
        return False

    if re.search(r"\d{4,}", termo_normalizado):
        return False

    if "gmail" in termo_normalizado:
        return False

    if "linkedin" in termo_normalizado:
        return False

    return True


def limpar_lista_termos(termos):
    resultado = []

    for termo in termos:
        termo = limpar_termo(termo)

        if not termo_valido(termo):
            continue

        if len(termo.split()) > 5:
            termo = " ".join(termo.split()[:5])

        resultado.append(termo)

    return remover_duplicados(resultado)


def remover_duplicados(lista):
    vistos = set()
    resultado = []

    for item in lista:
        chave = normalizar_texto(item)

        if chave not in vistos:
            vistos.add(chave)
            resultado.append(item)

    return resultado