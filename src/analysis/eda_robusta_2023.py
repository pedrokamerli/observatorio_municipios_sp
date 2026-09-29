from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARQUIVO = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "base_analitica_sp_2023_com_populacao.csv"
)


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(ARQUIVO)


# ============================================================
# 3. VARIÁVEIS PRINCIPAIS
# ============================================================

variaveis = [
    "populacao_2022",
    "pib",
    "pib_per_capita",
    "admissoes",
    "desligamentos",
    "saldo_empregos",
    "saldo_empregos_por_1000_hab",
]


# ============================================================
# 4. CORRELAÇÃO DE PEARSON
# ============================================================

pearson = (
    df[variaveis]
    .corr(method="pearson")
)

print("\n" + "=" * 60)
print("CORRELAÇÃO DE PEARSON")
print("=" * 60)

print(
    pearson.round(3)
)


# ============================================================
# 5. CORRELAÇÃO DE SPEARMAN
# ============================================================

spearman = (
    df[variaveis]
    .corr(method="spearman")
)

print("\n" + "=" * 60)
print("CORRELAÇÃO DE SPEARMAN")
print("=" * 60)

print(
    spearman.round(3)
)


# ============================================================
# 6. COMPARAÇÃO PEARSON X SPEARMAN
# ============================================================

print("\n" + "=" * 60)
print("PIB PER CAPITA X SALDO POR 1.000 HABITANTES")
print("=" * 60)

print(
    "Pearson:",
    round(
        pearson.loc[
            "pib_per_capita",
            "saldo_empregos_por_1000_hab"
        ],
        3
    )
)

print(
    "Spearman:",
    round(
        spearman.loc[
            "pib_per_capita",
            "saldo_empregos_por_1000_hab"
        ],
        3
    )
)


# ============================================================
# 7. TRANSFORMAÇÕES LOGARÍTMICAS
# ============================================================

df["log_populacao"] = np.log1p(
    df["populacao_2022"]
)

df["log_pib"] = np.log1p(
    df["pib"]
)

df["log_admissoes"] = np.log1p(
    df["admissoes"]
)

df["log_desligamentos"] = np.log1p(
    df["desligamentos"]
)


# ============================================================
# 8. CORRELAÇÃO COM VARIÁVEIS EM LOG
# ============================================================

variaveis_log = [
    "log_populacao",
    "log_pib",
    "pib_per_capita",
    "log_admissoes",
    "log_desligamentos",
    "saldo_empregos_por_1000_hab",
]

correlacao_log = (
    df[variaveis_log]
    .corr()
)

print("\n" + "=" * 60)
print("CORRELAÇÃO APÓS TRANSFORMAÇÃO LOG")
print("=" * 60)

print(
    correlacao_log.round(3)
)


# ============================================================
# 9. DETECÇÃO DE OUTLIERS COM IQR
# ============================================================

def detectar_outliers_iqr(dataframe, coluna):

    q1 = dataframe[coluna].quantile(0.25)
    q3 = dataframe[coluna].quantile(0.75)

    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = dataframe[
        (dataframe[coluna] < limite_inferior)
        |
        (dataframe[coluna] > limite_superior)
    ]

    return outliers


# ============================================================
# 10. OUTLIERS DO SALDO POR 1.000
# ============================================================

outliers_saldo = detectar_outliers_iqr(
    df,
    "saldo_empregos_por_1000_hab"
)

print("\n" + "=" * 60)
print("OUTLIERS - SALDO POR 1.000 HABITANTES")
print("=" * 60)

print("\nQuantidade:")
print(
    len(outliers_saldo)
)

print(
    outliers_saldo[
        [
            "municipio",
            "populacao_2022",
            "pib_per_capita",
            "saldo_empregos",
            "saldo_empregos_por_1000_hab",
        ]
    ]
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# 11. OUTLIERS DO PIB PER CAPITA
# ============================================================

outliers_pib_pc = detectar_outliers_iqr(
    df,
    "pib_per_capita"
)

print("\n" + "=" * 60)
print("OUTLIERS - PIB PER CAPITA")
print("=" * 60)

print("\nQuantidade:")
print(
    len(outliers_pib_pc)
)

print(
    outliers_pib_pc[
        [
            "municipio",
            "populacao_2022",
            "pib_per_capita",
            "saldo_empregos_por_1000_hab",
        ]
    ]
    .sort_values(
        "pib_per_capita",
        ascending=False
    )
    .to_string(index=False)
)


print("\nAnálise robusta concluída com sucesso.")