from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

arquivo_ibge = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ibge_municipios_sp.csv"
)


# ============================================================
# 2. LEITURA DA BASE DE MUNICÍPIOS
# ============================================================

municipios = pd.read_csv(
    arquivo_ibge
)


# ============================================================
# 3. CRIAÇÃO DO CÓDIGO DE 6 DÍGITOS
# ============================================================

municipios["codigo_caged"] = (
    municipios["id"] // 10
)


# ============================================================
# 4. SELEÇÃO E PADRONIZAÇÃO
# ============================================================

mapa = municipios[
    ["codigo_caged", "id", "nome"]
].copy()

mapa = mapa.rename(
    columns={
        "id": "codigo_ibge",
        "nome": "municipio"
    }
)


# ============================================================
# 5. VALIDAÇÕES
# ============================================================

print("\nPrimeiras linhas:")
print(mapa.head())

print("\nDimensão:")
print(mapa.shape)

print("\nCódigos CAGED únicos:")
print(mapa["codigo_caged"].nunique())

print("\nCódigos IBGE únicos:")
print(mapa["codigo_ibge"].nunique())

print("\nDuplicidades código CAGED:")
print(
    mapa["codigo_caged"]
    .duplicated()
    .sum()
)
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

arquivo_saida = PROCESSED_DIR / "mapa_municipios_sp.csv"

mapa.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)

print("\nMapa salvo em:")
print(arquivo_saida)