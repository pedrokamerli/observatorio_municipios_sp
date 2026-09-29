from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

ARQUIVO_BASE = (
    PROCESSED_DIR
    / "base_analitica_sp_2023.csv"
)

ARQUIVO_POPULACAO = (
    PROCESSED_DIR
    / "ibge_populacao_sp_2022.csv"
)

ARQUIVO_SAIDA = (
    PROCESSED_DIR
    / "base_analitica_sp_2023_com_populacao.csv"
)


# ============================================================
# 2. LEITURA
# ============================================================

base = pd.read_csv(
    ARQUIVO_BASE
)

populacao = pd.read_csv(
    ARQUIVO_POPULACAO
)


print("\nBase analítica:")
print(base.shape)

print("\nPopulação:")
print(populacao.shape)


# ============================================================
# 3. SELEÇÃO DAS COLUNAS DE POPULAÇÃO
# ============================================================

populacao = populacao[
    [
        "codigo_ibge",
        "populacao_2022",
        "ano_populacao",
    ]
].copy()


# ============================================================
# 4. PADRONIZAÇÃO DAS CHAVES
# ============================================================

base["codigo_ibge"] = (
    base["codigo_ibge"]
    .astype("int64")
)

populacao["codigo_ibge"] = (
    populacao["codigo_ibge"]
    .astype("int64")
)


# ============================================================
# 5. MERGE
# ============================================================

base = base.merge(
    populacao,
    on="codigo_ibge",
    how="left",
    validate="one_to_one",
    indicator=True
)


# ============================================================
# 6. VALIDAÇÃO DO MERGE
# ============================================================

print("\nResultado do merge:")

print(
    base["_merge"]
    .value_counts()
)

print("\nPopulação ausente:")

print(
    base["populacao_2022"]
    .isna()
    .sum()
)

if base["populacao_2022"].isna().sum() > 0:
    raise ValueError(
        "Existem municípios sem população."
    )


# ============================================================
# 7. REMOVE COLUNA TÉCNICA
# ============================================================

base = base.drop(
    columns="_merge"
)


# ============================================================
# 8. CRIAÇÃO DOS INDICADORES POR 1.000 HABITANTES
# ============================================================

base["admissoes_por_1000_hab"] = (
    base["admissoes"]
    / base["populacao_2022"]
    * 1000
)

base["desligamentos_por_1000_hab"] = (
    base["desligamentos"]
    / base["populacao_2022"]
    * 1000
)

base["saldo_empregos_por_1000_hab"] = (
    base["saldo_empregos"]
    / base["populacao_2022"]
    * 1000
)


# ============================================================
# 9. ARREDONDAMENTO
# ============================================================

colunas_taxas = [
    "admissoes_por_1000_hab",
    "desligamentos_por_1000_hab",
    "saldo_empregos_por_1000_hab",
]

base[colunas_taxas] = (
    base[colunas_taxas]
    .round(2)
)


# ============================================================
# 10. VALIDAÇÕES
# ============================================================

print("\nDimensão final:")
print(
    base.shape
)

print("\nMunicípios únicos:")
print(
    base["codigo_ibge"]
    .nunique()
)

print("\nDuplicidades:")
print(
    base["codigo_ibge"]
    .duplicated()
    .sum()
)

print("\nValores ausentes:")
print(
    base.isna().sum()
)


# ============================================================
# 11. MAIORES SALDOS ABSOLUTOS
# ============================================================

print("\n" + "=" * 60)
print("MAIORES SALDOS ABSOLUTOS")
print("=" * 60)

print(
    base[
        [
            "municipio",
            "populacao_2022",
            "saldo_empregos",
        ]
    ]
    .sort_values(
        "saldo_empregos",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 12. MAIORES SALDOS POR 1.000 HABITANTES
# ============================================================

print("\n" + "=" * 60)
print("MAIORES SALDOS POR 1.000 HABITANTES")
print("=" * 60)

print(
    base[
        [
            "municipio",
            "populacao_2022",
            "saldo_empregos",
            "saldo_empregos_por_1000_hab",
        ]
    ]
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 13. MENORES SALDOS POR 1.000 HABITANTES
# ============================================================

print("\n" + "=" * 60)
print("MENORES SALDOS POR 1.000 HABITANTES")
print("=" * 60)

print(
    base[
        [
            "municipio",
            "populacao_2022",
            "saldo_empregos",
            "saldo_empregos_por_1000_hab",
        ]
    ]
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=True
    )
    .head(10)
    .to_string(index=False)
)


# ============================================================
# 14. ORGANIZAÇÃO DAS COLUNAS
# ============================================================

base = base[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "populacao_2022",
        "ano_populacao",
        "pib",
        "pib_per_capita",
        "admissoes",
        "desligamentos",
        "saldo_empregos",
        "admissoes_por_1000_hab",
        "desligamentos_por_1000_hab",
        "saldo_empregos_por_1000_hab",
    ]
]


# ============================================================
# 15. SALVAMENTO
# ============================================================

base.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 60)
print("ARQUIVO GERADO")
print("=" * 60)

print("\nCaminho:")
print(
    ARQUIVO_SAIDA
)

print("\nArquivo existe?")
print(
    ARQUIVO_SAIDA.exists()
)

print("\nProcessamento concluído com sucesso.")