from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

arquivo = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
    / "2023"
    / "202301"
    / "CAGEDMOV202301.txt"
)


# ============================================================
# 2. LEITURA DO ARQUIVO DO NOVO CAGED
# ============================================================

df = pd.read_csv(
    arquivo,
    sep=";",
    encoding="utf-8"
)


# ============================================================
# 3. DATA UNDERSTANDING
# ============================================================

print("\nPrimeiras linhas:")
print(df.head())

print("\nDimensão:")
print(df.shape)

print("\nColunas:")
print(df.columns.tolist())

print("\nInformações do DataFrame:")
df.info()

print("\nQuantidade de valores nulos por coluna:")
print(df.isna().sum())

# ============================================================
# 4. INSPEÇÃO DAS VARIÁVEIS PRINCIPAIS
# ============================================================

print("\nCompetências encontradas:")
print(df["competênciamov"].value_counts())

print("\nUFs encontradas:")
print(df["uf"].value_counts().sort_index())

print("\nPrimeiros códigos de município:")
print(df["município"].head(20))

print("\nValores de saldo movimentação:")
print(df["saldomovimentação"].value_counts())

print("\nTipos de movimentação:")
print(
    df["tipomovimentação"]
    .value_counts()
    .sort_index()
)