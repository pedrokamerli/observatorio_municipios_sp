from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

arquivo = PROJECT_ROOT / "data" / "raw" / "pib_municipios_ibge.xlsx"

xls = pd.ExcelFile(arquivo)

print("Abas encontradas:")
print(xls.sheet_names)
df = pd.read_excel(
    arquivo,
    sheet_name="PIB dos Municípios"
)

print("\nPrimeiras linhas:")
print(df.head())

print("\nDimensão:")
print(df.shape)

print("\nColunas:")
print(df.columns.tolist())

print("\nInformações do DataFrame:")
print(df.info())

# ============================================================
# INVESTIGAÇÃO DA COBERTURA DOS DADOS
# ============================================================

print("\nAnos disponíveis:")
print(sorted(df["Ano"].unique()))

print("\nQuantidade de anos:")
print(df["Ano"].nunique())

print("\nEstados disponíveis:")
print(sorted(df["Sigla da Unidade da Federação"].unique()))

print("\nQuantidade de UFs:")
print(df["Sigla da Unidade da Federação"].nunique())

print("\nQuantidade de registros por ano:")
print(df["Ano"].value_counts().sort_index())

sp = df[
    df["Sigla da Unidade da Federação"] == "SP"
].copy()

print("\nDimensão da base de São Paulo:")
print(sp.shape)

print("\nQuantidade de municípios únicos de SP:")
print(sp["Código do Município"].nunique())

print("\nRegistros de SP por ano:")
print(sp["Ano"].value_counts().sort_index())

duplicados = sp.duplicated(
    subset=["Código do Município", "Ano"]
).sum()

print("\nDuplicidades Município + Ano:")
print(duplicados)
coluna_industria = (
    "Valor adicionado bruto da Indústria,\n"
    "a preços correntes\n"
    "(R$ 1.000)"
)

print("\nValores ausentes de indústria por ano:")

print(
    df.groupby("Ano")[coluna_industria]
      .apply(lambda x: x.isna().sum())
)
print(sorted(df["Ano"].unique()))
print(df["Ano"].nunique())

sp = df[df["Sigla da Unidade da Federação"] == "SP"].copy()

print(sp.shape)
print(sp["Código do Município"].nunique())
print(sp["Ano"].value_counts().sort_index())

print(
    sp.duplicated(
        subset=["Código do Município", "Ano"]
    ).sum()
)
# ============================================================
#  LEITURA DAS NOTAS DA BASE
# ============================================================

notas = pd.read_excel(
    arquivo,
    sheet_name="Notas",
    header=None
)

print("\nPrimeiras linhas da aba Notas:")
print(notas.head(30).to_string(index=False, header=False))
# ============================================================
# VERIFICAÇÃO DAS VARIÁVEIS ECONÔMICAS
# ============================================================

colunas_economicas = [
    "Valor adicionado bruto da Agropecuária, \na preços correntes\n(R$ 1.000)",
    "Valor adicionado bruto da Indústria,\na preços correntes\n(R$ 1.000)",
    "Valor adicionado bruto dos Serviços,\na preços correntes \n- exceto Administração, defesa, educação e saúde públicas e seguridade social\n(R$ 1.000)",
    "Valor adicionado bruto da Administração, defesa, educação e saúde públicas e seguridade social, \na preços correntes\n(R$ 1.000)",
    "Produto Interno Bruto, \na preços correntes\n(R$ 1.000)",
    "Produto Interno Bruto per capita, \na preços correntes\n(R$ 1,00)",
]

print("\nValores ausentes por ano em São Paulo:")

for coluna in colunas_economicas:

    print("\n", coluna)

    print(
        sp.groupby("Ano")[coluna]
        .apply(lambda x: x.isna().sum())
    )