from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "pib_municipios_ibge.xlsx"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA DA BASE ORIGINAL
# ============================================================

df = pd.read_excel(
    RAW_FILE,
    sheet_name="PIB dos Municípios"
)


# ============================================================
# 3. FILTRO DO ESTADO DE SÃO PAULO
# ============================================================

sp = df[
    df["Sigla da Unidade da Federação"] == "SP"
].copy()


# ============================================================
# 4. SELEÇÃO DAS VARIÁVEIS
# ============================================================

colunas = [
    "Ano",
    "Código do Município",
    "Nome do Município",

    "Valor adicionado bruto da Agropecuária, \n"
    "a preços correntes\n"
    "(R$ 1.000)",

    "Valor adicionado bruto da Indústria,\n"
    "a preços correntes\n"
    "(R$ 1.000)",

    "Valor adicionado bruto dos Serviços,\n"
    "a preços correntes \n"
    "- exceto Administração, defesa, educação e saúde públicas e seguridade social\n"
    "(R$ 1.000)",

    "Valor adicionado bruto da Administração, defesa, educação e saúde públicas e seguridade social, \n"
    "a preços correntes\n"
    "(R$ 1.000)",

    "Produto Interno Bruto, \n"
    "a preços correntes\n"
    "(R$ 1.000)",

    "Produto Interno Bruto per capita, \n"
    "a preços correntes\n"
    "(R$ 1,00)",
]

sp = sp[colunas].copy()
# ============================================================
# 5. PADRONIZAÇÃO DOS NOMES DAS COLUNAS
# ============================================================

sp = sp.rename(
    columns={
        "Ano": "ano",
        "Código do Município": "codigo_ibge",
        "Nome do Município": "municipio",

        "Valor adicionado bruto da Agropecuária, \n"
        "a preços correntes\n"
        "(R$ 1.000)": "vab_agropecuaria",

        "Valor adicionado bruto da Indústria,\n"
        "a preços correntes\n"
        "(R$ 1.000)": "vab_industria",

        "Valor adicionado bruto dos Serviços,\n"
        "a preços correntes \n"
        "- exceto Administração, defesa, educação e saúde públicas e seguridade social\n"
        "(R$ 1.000)": "vab_servicos",

        "Valor adicionado bruto da Administração, defesa, educação e saúde públicas e seguridade social, \n"
        "a preços correntes\n"
        "(R$ 1.000)": "vab_administracao_publica",

        "Produto Interno Bruto, \n"
        "a preços correntes\n"
        "(R$ 1.000)": "pib",

        "Produto Interno Bruto per capita, \n"
        "a preços correntes\n"
        "(R$ 1,00)": "pib_per_capita",
    }
)
# ============================================================
# 6. VALIDAÇÕES
# ============================================================

print("\nPrimeiras linhas:")
print(sp.head())

print("\nDimensão:")
print(sp.shape)

print("\nColunas:")
print(sp.columns.tolist())

print("\nMunicípios únicos:")
print(sp["codigo_ibge"].nunique())

print("\nAnos:")
print(sorted(sp["ano"].unique()))

print("\nDuplicidades Município + Ano:")
print(
    sp.duplicated(
        subset=["codigo_ibge", "ano"]
    ).sum()
)

print("\nValores ausentes:")
print(sp.isna().sum())
# ============================================================
# 7. SALVAMENTO DA BASE PROCESSADA
# ============================================================

arquivo_saida = PROCESSED_DIR / "ibge_pib_sp.csv"

sp.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)

print("\nBase processada salva em:")
print(arquivo_saida)

print("\nArquivo criado?")
print(arquivo_saida.exists())