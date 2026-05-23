from pathlib import Path
import re
import unicodedata
from collections import Counter

from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer


STOPWORDS_PT = [
    "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
    "para", "por", "com", "sem", "uma", "um", "uns", "umas",
    "que", "e", "ou", "ao", "aos", "as", "os", "o", "a",
    "se", "sua", "seu", "suas", "seus", "como", "mais", "menos",
    "muito", "muita", "muitos", "muitas", "sobre", "entre",
    "apos", "após", "durante", "visando", "rotina", "trabalho",
    "experiencia", "experiência", "conhecimento", "atuando",
    "area", "área", "atuação", "atual", "conclusao", "conclusão",
]


def extrair_texto_curriculo(caminho_curriculo):
    caminho = Path(caminho_curriculo)

    if not caminho.exists():
        raise FileNotFoundError(f"Currículo não encontrado: {caminho}")

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

        return corrigir_texto_espacado("\n".join(textos))

    if extensao == ".docx":
        documento = Document(str(caminho))
        return "\n".join(
            p.text for p in documento.paragraphs if p.text.strip()
        )

    raise ValueError("Formato não suportado. Use .txt, .pdf ou .docx.")

def corrigir_texto_espacado(texto):
    linhas_corrigidas = []

    for linha in texto.splitlines():
        linha_original = linha

        letras = re.findall(r"[A-Za-zÀ-ÿ]", linha)
        palavras_normais = re.findall(r"[A-Za-zÀ-ÿ]{2,}", linha)

        if len(letras) >= 6 and len(palavras_normais) <= 1:
            linha = re.sub(r"(?<=\w)\s(?=\w)", "", linha)

        linhas_corrigidas.append(linha)

    texto_corrigido = "\n".join(linhas_corrigidas)

    texto_corrigido = re.sub(
        r"(?<=\b[A-Za-zÀ-ÿ])\s(?=[A-Za-zÀ-ÿ]\b)",
        "",
        texto_corrigido,
    )

    return texto_corrigido


def normalizar_texto(texto):
    texto = corrigir_texto_espacado(texto)

    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    texto = re.sub(r"[^a-zA-Z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def dividir_em_blocos(texto):
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    blocos = []

    bloco_atual = []

    for linha in linhas:
        if re.search(r"experiencias|experiências|formacao|formação|habilidades", linha, re.I):
            if bloco_atual:
                blocos.append(" ".join(bloco_atual))
                bloco_atual = []

        bloco_atual.append(linha)

    if bloco_atual:
        blocos.append(" ".join(bloco_atual))

    return blocos


def extrair_cargos_explicitos(texto):
    padroes = [
        r"área de atuação:\s*([^\n\r]+)",
        r"area de atuacao:\s*([^\n\r]+)",
        r"cargo:\s*([^\n\r]+)",
        r"função:\s*([^\n\r]+)",
        r"funcao:\s*([^\n\r]+)",
    ]

    cargos = []

    for padrao in padroes:
        encontrados = re.findall(padrao, texto, flags=re.I)

        for item in encontrados:
            item = item.strip()
            item = re.sub(r"\s+", " ", item)

            if len(item) >= 4:
                cargos.append(item)

    return remover_duplicados(cargos)


def extrair_frases_importantes(texto):
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    frases = []

    for linha in linhas:
        linha_limpa = re.sub(r"\s+", " ", linha)

        if len(linha_limpa.split()) >= 3:
            frases.append(linha_limpa)

    return frases


def extrair_keywords_tfidf(texto, limite=20):
    texto_normalizado = normalizar_texto(texto)

    # ==========================================
    # EXTRAIR PALAVRAS MANUALMENTE
    # ==========================================

    palavras = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        texto_normalizado
    )

    palavras_filtradas = []

    for palavra in palavras:

        if palavra in STOPWORDS_PT:
            continue

        if contem_numero_telefone_ou_email(
            palavra
        ):
            continue

        palavras_filtradas.append(
            palavra
        )

    # ==========================================
    # VALIDAR PALAVRAS
    # ==========================================

    if not palavras_filtradas:

        raise ValueError(
            "Nenhuma palavra relevante foi encontrada no currículo."
        )

    # ==========================================
    # CONTAGEM
    # ==========================================

    contagem = Counter(
        palavras_filtradas
    )

    palavras_ordenadas = [
        palavra
        for palavra, _
        in contagem.most_common(limite)
    ]

    # ==========================================
    # TF-IDF COMO COMPLEMENTO
    # ==========================================

    try:

        blocos = dividir_em_blocos(
            texto
        )

        if len(blocos) >= 2:

            vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=40,
            )

            matriz = vectorizer.fit_transform(
                blocos
            )

            termos_tfidf = (
                vectorizer
                .get_feature_names_out()
            )

            for termo in termos_tfidf:

                termo = termo.strip()

                if (
                    termo not in palavras_ordenadas
                    and len(termo) >= 4
                ):

                    palavras_ordenadas.append(
                        termo
                    )

    except Exception:
        pass

    return remover_duplicados(
        palavras_ordenadas
    )[:limite]


def gerar_termos_busca_curriculo(texto_curriculo, limite=8):
    if not texto_curriculo or len(texto_curriculo.strip()) < 50:
        raise ValueError(
            "O texto extraído do currículo está vazio ou muito curto."
        )

    cargos = extrair_cargos_explicitos(texto_curriculo)
    keywords = extrair_keywords_tfidf(texto_curriculo)

    termos_busca = []

    for cargo in cargos:
        termos_busca.append(limpar_termo_busca(cargo))

    termos_profissionais = gerar_termos_profissionais_por_contexto(
        texto_curriculo,
        keywords,
    )

    termos_busca.extend(termos_profissionais)

    for keyword in keywords:
        if len(keyword.split()) >= 2:
            termos_busca.append(limpar_termo_busca(keyword))

    termos_busca = limpar_lista_termos(termos_busca)

    if not termos_busca:
        raise ValueError(
            "Nenhum termo relevante foi encontrado no currículo. "
            "Verifique se o PDF está sendo lido corretamente ou se o currículo "
            "possui experiências, cargos, formação e atividades profissionais."
        )

    return termos_busca[:limite]


def gerar_termos_profissionais_por_contexto(texto, keywords):
    texto_normalizado = normalizar_texto(texto)
    keywords_normalizadas = [normalizar_texto(k) for k in keywords]

    contexto = " ".join(keywords_normalizadas) + " " + texto_normalizado

    termos = []

    grupos = {
        "Auxiliar Administrativo": [
            "administrativo", "cadastro", "planilhas", "excel", "contrato",
            "chamados", "organizacao"
        ],
        "Recepcionista": [
            "recepcao", "primeiro atendimento", "atendimento", "cliente",
            "paciente"
        ],
        "Atendente Clínica": [
            "paciente", "consulta", "consultorio", "clinica", "guias",
            "agendamento"
        ],
        "Auxiliar de Consultório": [
            "consultorio", "exames", "tonometria", "retinografia",
            "acuidade visual"
        ],
        "Assistente de Qualidade": [
            "qualidade", "ona", "acreditacao"
        ],
        "Assistente Comercial": [
            "crm", "inside sales", "vendas", "negociacao", "comercial"
        ],
        "Estágio Fonoaudiologia": [
            "fonoaudiologia", "neurodesenvolvimento"
        ],
    }

    for cargo, sinais in grupos.items():
        pontos = 0

        for sinal in sinais:
            if normalizar_texto(sinal) in contexto:
                pontos += 1

        if pontos >= 2:
            termos.append(cargo)

    return termos


def extrair_skills(texto_curriculo):
    return gerar_termos_busca_curriculo(texto_curriculo)


def limpar_termo_busca(termo):
    termo = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s/-]", " ", termo)
    termo = re.sub(r"\s+", " ", termo).strip()

    palavras = termo.split()

    if len(palavras) > 5:
        termo = " ".join(palavras[:5])

    return termo


def limpar_lista_termos(termos):
    termos_limpos = []

    for termo in termos:
        termo = limpar_termo_busca(termo)

        if len(termo) < 4:
            continue

        if termo.lower() in STOPWORDS_PT:
            continue

        termos_limpos.append(termo)

    return remover_duplicados(termos_limpos)


def remover_duplicados(lista):
    vistos = set()
    resultado = []

    for item in lista:
        chave = normalizar_texto(item)

        if chave not in vistos:
            vistos.add(chave)
            resultado.append(item)

    return resultado


def contem_numero_telefone_ou_email(texto):
    if "@" in texto:
        return True

    if re.search(r"\d{4,}", texto):
        return True

    return False