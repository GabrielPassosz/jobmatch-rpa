from pathlib import Path

import pandas as pd


# ==========================================
# SALVAR VAGAS NO EXCEL
# ==========================================

def salvar_vagas_excel(
    vagas,
    caminho_excel="C:\\Users\\Pichau\\Desktop\\jobmatch-rpa\\entrada\\vagas.xlsx",
):
    caminho = Path(
        caminho_excel
    )

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==================================
    # DATAFRAME
    # ==================================

    df = pd.DataFrame(vagas)

    # ==================================
    # REMOVER DUPLICADAS
    # ==================================

    if not df.empty:

        df = df.drop_duplicates(
            subset=[
                "Cargo",
                "Empresa",
                "Link",
            ]
        )

    # ==================================
    # SALVAR EXCEL
    # ==================================

    df.to_excel(
        caminho,
        index=False,
    )

    print(
        f"\n✅ Vagas salvas em: "
        f"{caminho}"
    )

    print(
        f"Total de vagas: "
        f"{len(df)}"
    )

    return caminho