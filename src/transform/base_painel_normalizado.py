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

PAINEL_FILE = (
    PROCESSED_DIR
    / "base_painel_sp_2020_2023.csv"
)

POP_FILE = (
    PROCESSED_DIR
    / "ibge_populacao_sp_2022.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "base_painel_normalizado_sp_2020_2023.csv"
)


# ============================================================
# 2. LEITURA
# ============================================================

painel = pd.read_csv(
    PAINEL_FILE
)

populacao = pd.read_csv(
    POP_FILE
)


print("\n" + "=" * 60)
print("BASES CARREGADAS")
print("=" * 60)

print("\nPainel:")
print(
    painel.shape
)

print("\nPopulação:")
print(
    populacao.shape
)


# ============================================================
# 3. POPULAÇÃO BASE
# ============================================================

populacao = populacao[
    [
        "codigo_ibge",
        "populacao_2022",
    ]
].copy()


print("\nMunicípios na população:")
print(
    populacao[
        "codigo_ibge"
    ]
    .nunique()
)

print("\nDuplicidades população:")
print(
    populacao[
        "codigo_ibge"
    ]
    .duplicated()
    .sum()
)


# ============================================================
# 4. MERGE
# ============================================================

df = painel.merge(
    populacao,
    on="codigo_ibge",
    how="left",
    validate="many_to_one",
    indicator=True
)


print("\n" + "=" * 60)
print("VALIDAÇÃO DO MERGE")
print("=" * 60)

print(
    df["_merge"]
    .value_counts()
)


if (
    df["_merge"]
    .ne("both")
    .any()
):

    raise ValueError(
        "Existem municípios sem população."
    )


df = df.drop(
    columns="_merge"
)


# ============================================================
# 5. INDICADORES POR 1.000 HABITANTES
# ============================================================

df[
    "admissoes_por_1000_hab"
] = (
    df["admissoes"]
    / df["populacao_2022"]
    * 1000
)


df[
    "desligamentos_por_1000_hab"
] = (
    df["desligamentos"]
    / df["populacao_2022"]
    * 1000
)


df[
    "saldo_por_1000_hab"
] = (
    df["saldo_empregos"]
    / df["populacao_2022"]
    * 1000
)


df[
    "movimentacoes_por_1000_hab"
] = (
    (
        df["admissoes"]
        + df["desligamentos"]
    )
    / df["populacao_2022"]
    * 1000
)


# ============================================================
# 6. LAGS NORMALIZADOS
# ============================================================

df = df.sort_values(
    [
        "codigo_ibge",
        "ano",
    ]
).reset_index(
    drop=True
)


df[
    "saldo_por_1000_ano_anterior"
] = (
    df
    .groupby("codigo_ibge")[
        "saldo_por_1000_hab"
    ]
    .shift(1)
)


df[
    "admissoes_por_1000_ano_anterior"
] = (
    df
    .groupby("codigo_ibge")[
        "admissoes_por_1000_hab"
    ]
    .shift(1)
)


df[
    "desligamentos_por_1000_ano_anterior"
] = (
    df
    .groupby("codigo_ibge")[
        "desligamentos_por_1000_hab"
    ]
    .shift(1)
)


# ============================================================
# 7. TARGET DO ANO SEGUINTE
# ============================================================

df[
    "saldo_por_1000_proximo_ano"
] = (
    df
    .groupby("codigo_ibge")[
        "saldo_por_1000_hab"
    ]
    .shift(-1)
)


df[
    "variacao_saldo_por_1000_proximo_ano"
] = (
    df[
        "saldo_por_1000_proximo_ano"
    ]
    - df[
        "saldo_por_1000_hab"
    ]
)


# ============================================================
# 8. VALIDAÇÕES
# ============================================================

print("\n" + "=" * 60)
print("BASE NORMALIZADA")
print("=" * 60)

print("\nDimensão:")
print(
    df.shape
)

print("\nRegistros por ano:")
print(
    df
    .groupby("ano")
    .size()
)

print("\nMunicípios por ano:")
print(
    df
    .groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)


duplicidades = (
    df
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)


print("\nDuplicidades:")
print(
    duplicidades
)


if duplicidades != 0:

    raise ValueError(
        "Existem duplicidades."
    )


if len(df) != 2580:

    raise ValueError(
        f"Esperadas 2580 linhas. "
        f"Encontradas: {len(df)}"
    )


# ============================================================
# 9. RESUMO DOS INDICADORES
# ============================================================

print("\n" + "=" * 60)
print("RESUMO DOS INDICADORES")
print("=" * 60)

print(
    df.groupby("ano")[
        [
            "admissoes_por_1000_hab",
            "desligamentos_por_1000_hab",
            "saldo_por_1000_hab",
        ]
    ]
    .agg(
        [
            "mean",
            "median",
            "min",
            "max",
        ]
    )
)


# ============================================================
# 10. EXEMPLO BAURU
# ============================================================

print("\n" + "=" * 60)
print("BAURU")
print("=" * 60)

print(
    df[
        df["municipio"]
        .str.lower()
        .eq("bauru")
    ][
        [
            "ano",
            "populacao_2022",
            "admissoes",
            "desligamentos",
            "saldo_empregos",
            "saldo_por_1000_hab",
            "saldo_por_1000_ano_anterior",
            "saldo_por_1000_proximo_ano",
            "variacao_saldo_por_1000_proximo_ano",
        ]
    ]
    .to_string(
        index=False
    )
)


# ============================================================
# 11. SALVAMENTO
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 60)
print("ARQUIVO GERADO")
print("=" * 60)

print(
    OUTPUT_FILE
)

print("\nExiste?")
print(
    OUTPUT_FILE.exists()
)

print(
    "\nBase normalizada criada com sucesso."
)