from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

ANO_ANALISE = 2023


# ============================================================
# 2. CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

ARQUIVO_PIB = (
    PROCESSED_DIR
    / "ibge_pib_sp.csv"
)

ARQUIVO_CAGED = (
    PROCESSED_DIR
    / "caged_sp_2023.csv"
)

ARQUIVO_SAIDA = (
    PROCESSED_DIR
    / "base_analitica_sp_2023.csv"
)


# ============================================================
# 3. VALIDAÇÃO DOS ARQUIVOS
# ============================================================

if not ARQUIVO_PIB.exists():
    raise FileNotFoundError(
        f"Arquivo do PIB não encontrado: {ARQUIVO_PIB}"
    )

if not ARQUIVO_CAGED.exists():
    raise FileNotFoundError(
        f"Arquivo do CAGED não encontrado: {ARQUIVO_CAGED}"
    )


# ============================================================
# 4. LEITURA DAS BASES
# ============================================================

pib = pd.read_csv(
    ARQUIVO_PIB
)

caged = pd.read_csv(
    ARQUIVO_CAGED
)


print("\n" + "=" * 60)
print("BASES CARREGADAS")
print("=" * 60)

print("\nPIB:")
print(pib.shape)

print("\nCAGED:")
print(caged.shape)


# ============================================================
# 5. INSPEÇÃO DAS COLUNAS
# ============================================================

print("\nColunas do PIB:")
print(
    pib.columns.tolist()
)

print("\nColunas do CAGED:")
print(
    caged.columns.tolist()
)


# ============================================================
# 6. FILTRO DO PIB PARA 2023
# ============================================================

pib_2023 = pib[
    pib["ano"] == ANO_ANALISE
].copy()


print("\n" + "=" * 60)
print("PIB 2023")
print("=" * 60)

print("\nDimensão:")
print(
    pib_2023.shape
)

print("\nMunicípios únicos:")
print(
    pib_2023["codigo_ibge"]
    .nunique()
)

print("\nDuplicidades Município + Ano:")
print(
    pib_2023
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)


# ============================================================
# 7. SELEÇÃO DAS VARIÁVEIS DO PIB
# ============================================================

# Em 2023 o arquivo do IBGE possui PIB e PIB per capita.
# Os componentes de VAB não serão usados neste primeiro merge,
# pois não foram publicados para 2023 na mesma base.

pib_2023 = pib_2023[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "pib",
        "pib_per_capita",
    ]
].copy()


# ============================================================
# 8. VALIDAÇÃO DA BASE DO CAGED
# ============================================================

print("\n" + "=" * 60)
print("CAGED 2023")
print("=" * 60)

print("\nDimensão:")
print(
    caged.shape
)

print("\nMunicípios únicos:")
print(
    caged["codigo_ibge"]
    .nunique()
)

print("\nAnos encontrados:")
print(
    sorted(
        caged["ano"]
        .unique()
    )
)

print("\nDuplicidades Município + Ano:")
print(
    caged
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)


# ============================================================
# 9. SELEÇÃO DAS VARIÁVEIS DO CAGED
# ============================================================

caged_2023 = caged[
    [
        "ano",
        "codigo_ibge",
        "admissoes",
        "desligamentos",
        "saldo_empregos",
    ]
].copy()


# ============================================================
# 10. PADRONIZAÇÃO DOS TIPOS DAS CHAVES
# ============================================================

pib_2023["codigo_ibge"] = (
    pib_2023["codigo_ibge"]
    .astype("int64")
)

caged_2023["codigo_ibge"] = (
    caged_2023["codigo_ibge"]
    .astype("int64")
)

pib_2023["ano"] = (
    pib_2023["ano"]
    .astype("int64")
)

caged_2023["ano"] = (
    caged_2023["ano"]
    .astype("int64")
)


# ============================================================
# 11. MERGE PIB + CAGED
# ============================================================

base_analitica = pib_2023.merge(
    caged_2023,
    on=[
        "codigo_ibge",
        "ano",
    ],
    how="left",
    validate="one_to_one",
    indicator=True
)


# ============================================================
# 12. VALIDAÇÃO DO MERGE
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DO MERGE PIB + CAGED")
print("=" * 60)

print("\nResultado do merge:")
print(
    base_analitica["_merge"]
    .value_counts()
)

print("\nDimensão após o merge:")
print(
    base_analitica.shape
)

print("\nMunicípios únicos:")
print(
    base_analitica[
        "codigo_ibge"
    ]
    .nunique()
)


# ============================================================
# 13. MUNICÍPIOS SEM CORRESPONDÊNCIA
# ============================================================

nao_encontrados = base_analitica[
    base_analitica["_merge"]
    != "both"
]

print("\nMunicípios sem correspondência:")
print(
    len(nao_encontrados)
)

if len(nao_encontrados) > 0:

    print(
        nao_encontrados[
            [
                "codigo_ibge",
                "municipio",
                "_merge",
            ]
        ]
    )

    raise ValueError(
        "Existem municípios do PIB sem correspondência no CAGED."
    )


# ============================================================
# 14. REMOÇÃO DA COLUNA TÉCNICA
# ============================================================

base_analitica = base_analitica.drop(
    columns="_merge"
)


# ============================================================
# 15. VALIDAÇÃO DE VALORES AUSENTES
# ============================================================

print("\n" + "=" * 60)
print("VALORES AUSENTES")
print("=" * 60)

print(
    base_analitica
    .isna()
    .sum()
)


# ============================================================
# 16. VALIDAÇÃO DE DUPLICIDADES
# ============================================================

duplicidades = (
    base_analitica
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)

print("\nDuplicidades Município + Ano:")
print(
    duplicidades
)

if duplicidades > 0:
    raise ValueError(
        "Foram encontradas duplicidades na base analítica."
    )


# ============================================================
# 17. VALIDAÇÕES MATEMÁTICAS DO CAGED
# ============================================================

base_analitica[
    "saldo_calculado"
] = (
    base_analitica[
        "admissoes"
    ]
    -
    base_analitica[
        "desligamentos"
    ]
)

saldo_incorreto = (
    base_analitica[
        "saldo_calculado"
    ]
    !=
    base_analitica[
        "saldo_empregos"
    ]
)

print("\nMunicípios com saldo divergente:")
print(
    saldo_incorreto.sum()
)

if saldo_incorreto.any():
    raise ValueError(
        "Existem municípios com saldo de empregos divergente."
    )


# A coluna foi criada somente para validação
base_analitica = base_analitica.drop(
    columns="saldo_calculado"
)


# ============================================================
# 18. ORGANIZAÇÃO DAS COLUNAS
# ============================================================

base_analitica = base_analitica[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "pib",
        "pib_per_capita",
        "admissoes",
        "desligamentos",
        "saldo_empregos",
    ]
].sort_values(
    "codigo_ibge"
).reset_index(
    drop=True
)


# ============================================================
# 19. RESUMO DA BASE ANALÍTICA
# ============================================================

print("\n" + "=" * 60)
print("BASE ANALÍTICA FINAL")
print("=" * 60)

print("\nPrimeiras linhas:")
print(
    base_analitica.head()
)

print("\nDimensão:")
print(
    base_analitica.shape
)

print("\nMunicípios únicos:")
print(
    base_analitica[
        "codigo_ibge"
    ]
    .nunique()
)

print("\nAnos:")
print(
    sorted(
        base_analitica[
            "ano"
        ]
        .unique()
    )
)

print("\nValores ausentes:")
print(
    base_analitica
    .isna()
    .sum()
)


# ============================================================
# 20. ESTATÍSTICAS INICIAIS
# ============================================================

print("\n" + "=" * 60)
print("ESTATÍSTICAS INICIAIS")
print("=" * 60)

print(
    base_analitica[
        [
            "pib",
            "pib_per_capita",
            "admissoes",
            "desligamentos",
            "saldo_empregos",
        ]
    ]
    .describe()
)


# ============================================================
# 21. SALVAMENTO
# ============================================================

base_analitica.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 22. CONFIRMAÇÃO
# ============================================================

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