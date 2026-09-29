from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

ANOS = [
    2020,
    2021,
    2022,
    2023,
]


# ============================================================
# 2. CAMINHOS
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
    / "caged_sp_anual_2020_2023.csv"
)

ARQUIVO_SAIDA = (
    PROCESSED_DIR
    / "base_painel_sp_2020_2023.csv"
)


# ============================================================
# 3. LEITURA
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
# 4. FILTRO DOS ANOS
# ============================================================

pib = pib[
    pib["ano"].isin(ANOS)
].copy()

caged = caged[
    caged["ano"].isin(ANOS)
].copy()


# ============================================================
# 5. VALIDAÇÃO PRÉ-MERGE
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO PRÉ-MERGE")
print("=" * 60)

print("\nPIB - registros por ano:")
print(
    pib.groupby("ano")
    .size()
)

print("\nCAGED - registros por ano:")
print(
    caged.groupby("ano")
    .size()
)

print("\nPIB - municípios por ano:")
print(
    pib.groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)

print("\nCAGED - municípios por ano:")
print(
    caged.groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)


# ============================================================
# 6. DUPLICIDADES
# ============================================================

duplicidades_pib = (
    pib.duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)

duplicidades_caged = (
    caged.duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)


print("\nDuplicidades PIB:")
print(duplicidades_pib)

print("\nDuplicidades CAGED:")
print(duplicidades_caged)


if duplicidades_pib != 0:
    raise ValueError(
        "Existem duplicidades na base do PIB."
    )

if duplicidades_caged != 0:
    raise ValueError(
        "Existem duplicidades na base do CAGED."
    )


# ============================================================
# 7. SELEÇÃO DAS COLUNAS
# ============================================================

pib = pib[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "vab_agropecuaria",
        "vab_industria",
        "vab_servicos",
        "vab_administracao_publica",
        "pib",
        "pib_per_capita",
    ]
].copy()


caged = caged[
    [
        "ano",
        "codigo_ibge",
        "admissoes",
        "desligamentos",
        "saldo_empregos",
    ]
].copy()


# ============================================================
# 8. MERGE
# ============================================================

painel = pib.merge(
    caged,
    on=[
        "codigo_ibge",
        "ano",
    ],
    how="left",
    validate="one_to_one",
    indicator=True
)


# ============================================================
# 9. VALIDAÇÃO DO MERGE
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DO MERGE")
print("=" * 60)

print("\nResultado:")
print(
    painel["_merge"]
    .value_counts()
)

print("\nDimensão:")
print(
    painel.shape
)


problemas = painel[
    painel["_merge"]
    != "both"
]

print("\nRegistros sem correspondência:")
print(
    len(problemas)
)


if len(problemas) > 0:

    print(
        problemas[
            [
                "ano",
                "codigo_ibge",
                "municipio",
                "_merge",
            ]
        ]
    )

    raise ValueError(
        "Existem registros sem correspondência."
    )


painel = painel.drop(
    columns="_merge"
)


# ============================================================
# 10. VALIDAÇÃO DOS 4 ANOS
# ============================================================

print("\nRegistros por ano:")

print(
    painel.groupby("ano")
    .size()
)

print("\nMunicípios por ano:")

print(
    painel.groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)


# ============================================================
# 11. VALORES AUSENTES
# ============================================================

print("\n" + "=" * 60)
print("VALORES AUSENTES POR ANO")
print("=" * 60)

for ano in ANOS:

    print(f"\nAno {ano}:")

    print(
        painel[
            painel["ano"] == ano
        ]
        .isna()
        .sum()
    )


# ============================================================
# 12. VARIAÇÃO DO PIB
# ============================================================

painel = painel.sort_values(
    [
        "codigo_ibge",
        "ano",
    ]
).reset_index(
    drop=True
)


painel["crescimento_pib_pct"] = (
    painel
    .groupby("codigo_ibge")[
        "pib"
    ]
    .pct_change(
        fill_method=None
    )
    * 100
)


painel[
    "crescimento_pib_per_capita_pct"
] = (
    painel
    .groupby("codigo_ibge")[
        "pib_per_capita"
    ]
    .pct_change(
        fill_method=None
    )
    * 100
)


# ============================================================
# 13. LAG DO EMPREGO
# ============================================================

painel[
    "saldo_empregos_ano_anterior"
] = (
    painel
    .groupby("codigo_ibge")[
        "saldo_empregos"
    ]
    .shift(1)
)


painel[
    "admissoes_ano_anterior"
] = (
    painel
    .groupby("codigo_ibge")[
        "admissoes"
    ]
    .shift(1)
)


painel[
    "desligamentos_ano_anterior"
] = (
    painel
    .groupby("codigo_ibge")[
        "desligamentos"
    ]
    .shift(1)
)


# ============================================================
# 14. TARGET: EMPREGO DO ANO SEGUINTE
# ============================================================

painel[
    "saldo_empregos_proximo_ano"
] = (
    painel
    .groupby("codigo_ibge")[
        "saldo_empregos"
    ]
    .shift(-1)
)


# ============================================================
# 15. ESTRUTURA ECONÔMICA
# ============================================================

painel[
    "participacao_agro_pct"
] = (
    painel["vab_agropecuaria"]
    / painel["pib"]
    * 100
)

painel[
    "participacao_industria_pct"
] = (
    painel["vab_industria"]
    / painel["pib"]
    * 100
)

painel[
    "participacao_servicos_pct"
] = (
    painel["vab_servicos"]
    / painel["pib"]
    * 100
)

painel[
    "participacao_adm_publica_pct"
] = (
    painel["vab_administracao_publica"]
    / painel["pib"]
    * 100
)


# ============================================================
# 16. RESUMO
# ============================================================

print("\n" + "=" * 60)
print("PAINEL ECONÔMICO FINAL")
print("=" * 60)

print("\nDimensão:")
print(
    painel.shape
)

print("\nPrimeiras linhas:")
print(
    painel.head(12)
)

print("\nAnos:")
print(
    sorted(
        painel["ano"]
        .unique()
    )
)

print("\nMunicípios:")
print(
    painel["codigo_ibge"]
    .nunique()
)


# ============================================================
# 17. VALIDAÇÃO DA DIMENSÃO
# ============================================================

linhas_esperadas = (
    645
    * len(ANOS)
)

print("\nLinhas esperadas:")
print(
    linhas_esperadas
)

print("\nLinhas encontradas:")
print(
    len(painel)
)


if len(painel) != linhas_esperadas:

    raise ValueError(
        "A dimensão do painel não corresponde ao esperado."
    )


# ============================================================
# 18. SALVAMENTO
# ============================================================

painel.to_csv(
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

print("\nExiste?")
print(
    ARQUIVO_SAIDA.exists()
)

print(
    "\nPainel 2020-2023 criado com sucesso."
)