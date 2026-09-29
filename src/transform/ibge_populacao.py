from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ibge_populacao_2022.csv"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "ibge_populacao_sp_2022.csv"
)


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(
    RAW_FILE,
    dtype={
        "D1C": "string",
        "D3C": "string"
    }
)

print("\nDimensão original:")
print(df.shape)


# ============================================================
# 3. FILTRO DO ESTADO DE SÃO PAULO
# ============================================================

sp = df[
    df["D1C"].str.startswith("35")
].copy()

print("\nDimensão SP:")
print(sp.shape)


# ============================================================
# 4. SELEÇÃO DAS COLUNAS
# ============================================================

sp = sp[
    [
        "D1C",
        "D1N",
        "V",
        "D3C",
    ]
].copy()


# ============================================================
# 5. RENOMEAR COLUNAS
# ============================================================

sp = sp.rename(
    columns={
        "D1C": "codigo_ibge",
        "D1N": "municipio_ibge",
        "V": "populacao_2022",
        "D3C": "ano_populacao",
    }
)


# ============================================================
# 6. PADRONIZAÇÃO DOS TIPOS
# ============================================================

sp["codigo_ibge"] = (
    sp["codigo_ibge"]
    .astype("int64")
)

sp["populacao_2022"] = pd.to_numeric(
    sp["populacao_2022"],
    errors="coerce"
)

sp["ano_populacao"] = (
    sp["ano_populacao"]
    .astype("int64")
)


# ============================================================
# 7. VALIDAÇÕES
# ============================================================

print("\nPrimeiras linhas:")
print(sp.head())

print("\nDimensão final:")
print(sp.shape)

print("\nMunicípios únicos:")
print(
    sp["codigo_ibge"]
    .nunique()
)

print("\nDuplicidades de código IBGE:")
print(
    sp["codigo_ibge"]
    .duplicated()
    .sum()
)

print("\nValores ausentes:")
print(
    sp.isna().sum()
)

print("\nAno encontrado:")
print(
    sp["ano_populacao"]
    .unique()
)

print("\nPopulação mínima:")
print(
    sp["populacao_2022"]
    .min()
)

print("\nPopulação máxima:")
print(
    sp["populacao_2022"]
    .max()
)


# ============================================================
# 8. VALIDAÇÕES OBRIGATÓRIAS
# ============================================================

if sp["codigo_ibge"].nunique() != 645:
    raise ValueError(
        "Quantidade de municípios de SP diferente de 645."
    )

if sp["codigo_ibge"].duplicated().sum() != 0:
    raise ValueError(
        "Existem códigos IBGE duplicados."
    )

if sp["populacao_2022"].isna().sum() != 0:
    raise ValueError(
        "Existem valores de população ausentes."
    )


# ============================================================
# 9. SALVAMENTO
# ============================================================

sp.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo salvo em:")
print(OUTPUT_FILE)

print("\nArquivo criado?")
print(
    OUTPUT_FILE.exists()
)

print("\nProcessamento concluído com sucesso.")