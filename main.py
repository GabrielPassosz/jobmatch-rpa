from datetime import datetime
from pathlib import Path

from src.config_loader import carregar_config
from src.logger_config import configurar_logger

from src.resume_analyzer import (
    extrair_texto_curriculo,
    extrair_skills,
)

from src.job_matcher import (
    carregar_vagas,
    analisar_vagas,
)

from src.excel_report import salvar_relatorio_excel
from src.linkedin_scraper import buscar_vagas_por_curriculo
from src.save_jobs_excel import salvar_vagas_excel


def main():
    config = carregar_config()

    logger = configurar_logger(
        config["PASTA_LOGS"]
    )

    logger.info("=" * 80)
    logger.info("INICIANDO JOBMATCH RPA")
    logger.info("=" * 80)

    try:
        logger.info("Lendo currículo...")

        texto_curriculo = extrair_texto_curriculo(
            config["CURRICULO"]
        )

        logger.info("Extraindo skills do currículo...")

        skills_curriculo = extrair_skills(
            texto_curriculo
        )

        logger.info(
            f"Skills encontradas: {skills_curriculo}"
        )

        if config["BUSCAR_VAGAS_REAIS"]:
            logger.info(
                "Buscando vagas reais no LinkedIn "
                "com base nas skills do currículo..."
            )

            vagas = buscar_vagas_por_curriculo(
                skills_curriculo=skills_curriculo,
                quantidade_por_termo=config["QUANTIDADE_VAGAS"],
                headless=False,
            )

            logger.info(
                f"Vagas coletadas do LinkedIn: {len(vagas)}"
            )

            if vagas.empty:
                logger.warning(
                    "Nenhuma vaga foi coletada no LinkedIn. "
                    "Verifique se a página carregou corretamente."
                )
                return

            salvar_vagas_excel(
                vagas=vagas,
                caminho_excel=config["VAGAS"],
            )

            logger.info(
                f"Planilha de vagas atualizada: {config['VAGAS']}"
            )

        else:
            logger.info("Lendo vagas da planilha local...")

            vagas = carregar_vagas(
                config["VAGAS"]
            )

            logger.info(
                f"Vagas carregadas da planilha: {len(vagas)}"
            )

        logger.info(
            "Calculando compatibilidade das vagas "
            "com o currículo..."
        )

        resultados = analisar_vagas(
            vagas=vagas,
            skills_curriculo=skills_curriculo,
            score_aplicar=int(config["SCORE_APLICAR"]),
            score_avaliar=int(config["SCORE_AVALIAR"]),
        )

        logger.info(
            f"Total de vagas analisadas: {len(resultados)}"
        )

        data_execucao = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        pasta_saida = (
            Path(config["PASTA_SAIDA"])
            / data_execucao
        )

        pasta_saida.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            f"Pasta de saída criada: {pasta_saida}"
        )

        caminho_relatorio = salvar_relatorio_excel(
            resultados=resultados,
            pasta_saida=pasta_saida,
        )

        logger.info(
            f"Relatório salvo em: {caminho_relatorio}"
        )

        logger.info("=" * 80)
        logger.info("JOBMATCH FINALIZADO COM SUCESSO")
        logger.info("=" * 80)

    except Exception as erro:
        logger.exception(
            f"Erro durante execução: {erro}"
        )
        raise


if __name__ == "__main__":
    main()