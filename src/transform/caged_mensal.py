from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARQUIVO = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
    / "2023"
    / "202301"
    / "CAGEDMOV202301.txt"
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. COLUNAS NECESSÁRIAS
# ============================================================

colunas = [
    "competênciamov",
    "uf",
    "município",
    "saldomovimentação",
]


# ============================================================
# 3. LEITURA OTIMIZADA
# ============================================================

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    encoding="utf-8",
    usecols=colunas
)


print("\nDimensão após carregar somente as colunas necessárias:")
print(df.shape)

print("\nUso de memória:")
df.info()
# ============================================================
# 4. FILTRO DO ESTADO DE SÃO PAULO
# ============================================================

sp = df[
    df["uf"] == 35
].copy()


print("\nMovimentações em São Paulo:")
print(sp.shape)

print("\nValores de saldo em SP:")
print(
    sp["saldomovimentação"]
    .value_counts()
)
# ============================================================
# 5. IDENTIFICAÇÃO DAS MOVIMENTAÇÕES
# ============================================================

sp["admissao"] = (
    sp["saldomovimentação"] == 1
).astype("int8")

sp["desligamento"] = (
    sp["saldomovimentação"] == -1
).astype("int8")
# ============================================================
# 6. AGREGAÇÃO POR MUNICÍPIO
# ============================================================

caged_municipal = (
    sp.groupby(
        ["competênciamov", "município"],
        as_index=False
    )
    .agg(
        admissoes=("admissao", "sum"),
        desligamentos=("desligamento", "sum"),
        saldo_empregos=("saldomovimentação", "sum"),
    )
)
# ============================================================
# 7. CRIAÇÃO DE ANO E MÊS
# ============================================================

caged_municipal["ano"] = (
    caged_municipal["competênciamov"] // 100
)

caged_municipal["mes"] = (
    caged_municipal["competênciamov"] % 100
)
caged_municipal = caged_municipal.rename(
    columns={
        "município": "codigo_caged"
    }
)

print("\nPrimeiras linhas do CAGED agregado:")
print(caged_municipal.head())

print("\nDimensão:")
print(caged_municipal.shape)

print("\nQuantidade de municípios com movimentação:")
print(
    caged_municipal["codigo_caged"]
    .nunique()
)

print("\nTotal de admissões:")
print(
    caged_municipal["admissoes"]
    .sum()
)

print("\nTotal de desligamentos:")
print(
    caged_municipal["desligamentos"]
    .sum()
)

print("\nSaldo total de empregos:")
print(
    caged_municipal["saldo_empregos"]
    .sum()
)
total_movimentacoes = (
    caged_municipal["admissoes"].sum()
    + caged_municipal["desligamentos"].sum()
)

print("\nTotal agregado de movimentações:")
print(total_movimentacoes)

print("\nTotal original de movimentações de SP:")
print(len(sp))

print("\nOs totais conferem?")
print(total_movimentacoes == len(sp))
# ============================================================
# 8. LEITURA DO MAPA CAGED -> IBGE
# ============================================================

arquivo_mapa = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mapa_municipios_sp.csv"
)

mapa = pd.read_csv(arquivo_mapa)
# ============================================================
# 9. MERGE COM CÓDIGO IBGE
# ============================================================

caged_municipal = caged_municipal.merge(
    mapa,
    on="codigo_caged",
    how="left",
    validate="one_to_one",
    indicator=True
)
print("\nResultado do merge:")
print(
    caged_municipal["_merge"]
    .value_counts()
)

print("\nCódigos IBGE ausentes:")
print(
    caged_municipal["codigo_ibge"]
    .isna()
    .sum()
)

print("\nDimensão após o merge:")
print(caged_municipal.shape)
# ============================================================
# 10. REMOÇÃO DA COLUNA TÉCNICA DO MERGE
# ============================================================

caged_municipal = caged_municipal.drop(
    columns="_merge"
)


# ============================================================
# 11. ORGANIZAÇÃO DAS COLUNAS
# ============================================================

caged_municipal = caged_municipal[
    [
        "ano",
        "mes",
        "competênciamov",
        "codigo_ibge",
        "codigo_caged",
        "municipio",
        "admissoes",
        "desligamentos",
        "saldo_empregos",
    ]
]


# ============================================================
# 12. SALVAMENTO
# ============================================================

arquivo_saida = (
    PROCESSED_DIR
    / "caged_sp_202301.csv"
)

caged_municipal.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)

print("\nBase CAGED mensal salva em:")
print(arquivo_saida)

print("\nArquivo criado?")
print(arquivo_saida.exists())

print("\nPrimeiras linhas da base final:")
print(caged_municipal.head())