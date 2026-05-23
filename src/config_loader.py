from configparser import ConfigParser
from pathlib import Path


def carregar_config():
    caminho_config = Path("config.ini")

    if not caminho_config.exists():
        raise FileNotFoundError("Arquivo config.ini não encontrado.")

    parser = ConfigParser()
    parser.read(caminho_config, encoding="utf-8")

    config = {
        "CURRICULO": parser.get("CAMINHOS", "CURRICULO"),
        "VAGAS": parser.get("CAMINHOS", "VAGAS"),
        "PASTA_SAIDA": parser.get("CAMINHOS", "PASTA_SAIDA"),
        "PASTA_LOGS": parser.get("CAMINHOS", "PASTA_LOGS"),
        "SCORE_APLICAR": parser.get("JOBMATCH", "SCORE_APLICAR"),
        "SCORE_AVALIAR": parser.get("JOBMATCH", "SCORE_AVALIAR"),
    }

    return config