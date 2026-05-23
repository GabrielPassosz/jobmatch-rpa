import logging
from pathlib import Path
from datetime import datetime


def configurar_logger(pasta_logs):
    # ==============================
    # CRIAR PASTA DE LOGS
    # ==============================

    Path(pasta_logs).mkdir(
        parents=True,
        exist_ok=True
    )

    # ==============================
    # NOME DO ARQUIVO DE LOG
    # ==============================

    data_log = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    caminho_log = (
        Path(pasta_logs)
        / f"jobmatch_{data_log}.log"
    )

    # ==============================
    # CRIAR LOGGER
    # ==============================

    logger = logging.getLogger(
        "JOBMATCH_RPA"
    )

    logger.setLevel(logging.INFO)

    # Evita logs duplicados
    logger.handlers.clear()

    # ==============================
    # FORMATAÇÃO
    # ==============================

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S"
    )

    # ==============================
    # FILE HANDLER
    # ==============================

    file_handler = logging.FileHandler(
        caminho_log,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    # ==============================
    # CONSOLE HANDLER
    # ==============================

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    # ==============================
    # ADICIONAR HANDLERS
    # ==============================

    logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger