from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARQUIVO = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "base_painel_normalizado_sp_2020_2023.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "analise_setorial"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(ARQUIVO)


print("\n" + "=" * 60)
print("BASE CARREGADA")
print("=" * 60)

print("\nDimensão:")
print(df.shape)


# ============================================================
# 3. FILTRO 2020-2021
# ============================================================

setorial = df[
    df["ano"].isin(
        [
            2020,
            2021,
        ]
    )
].copy()


print("\nRegistros por ano:")

print(
    setorial
    .groupby("ano")
    .size()
)


# ============================================================
# 4. VERIFICAÇÃO DOS VABs
# ============================================================

colunas_vab = [
    "vab_agropecuaria",
    "vab_industria",
    "vab_servicos",
    "vab_administracao_publica",
]


print("\n" + "=" * 60)
print("VALORES AUSENTES NOS VABs")
print("=" * 60)

print(
    setorial[
        colunas_vab
    ]
    .isna()
    .sum()
)


# ============================================================
# 5. PARTICIPAÇÃO DOS SETORES NO PIB
# ============================================================

setorial[
    "participacao_agro_pct"
] = (
    setorial["vab_agropecuaria"]
    / setorial["pib"]
    * 100
)


setorial[
    "participacao_industria_pct"
] = (
    setorial["vab_industria"]
    / setorial["pib"]
    * 100
)


setorial[
    "participacao_servicos_pct"
] = (
    setorial["vab_servicos"]
    / setorial["pib"]
    * 100
)


setorial[
    "participacao_adm_publica_pct"
] = (
    setorial["vab_administracao_publica"]
    / setorial["pib"]
    * 100
)


# ============================================================
# 6. SETOR DOMINANTE
# ============================================================

mapa_setores = {
    "participacao_agro_pct":
        "Agropecuária",

    "participacao_industria_pct":
        "Indústria",

    "participacao_servicos_pct":
        "Serviços",

    "participacao_adm_publica_pct":
        "Administração pública",
}


colunas_participacao = list(
    mapa_setores.keys()
)


setorial[
    "setor_dominante"
] = (
    setorial[
        colunas_participacao
    ]
    .idxmax(
        axis=1
    )
    .map(
        mapa_setores
    )
)


# ============================================================
# 7. RESUMO DA ESTRUTURA ECONÔMICA
# ============================================================

print("\n" + "=" * 60)
print("ESTRUTURA ECONÔMICA")
print("=" * 60)

print("\nSetor dominante por ano:")

print(
    pd.crosstab(
        setorial["ano"],
        setorial["setor_dominante"]
    )
)


# ============================================================
# 8. MEDIANAS DAS PARTICIPAÇÕES
# ============================================================

print("\n" + "=" * 60)
print("PARTICIPAÇÃO SETORIAL MEDIANA")
print("=" * 60)

print(
    setorial
    .groupby("ano")[
        colunas_participacao
    ]
    .median()
    .round(2)
)


# ============================================================
# 9. CORRELAÇÃO SETOR × EMPREGO
# ============================================================

variaveis_correlacao = [
    "participacao_agro_pct",
    "participacao_industria_pct",
    "participacao_servicos_pct",
    "participacao_adm_publica_pct",
    "saldo_por_1000_hab",
]


print("\n" + "=" * 60)
print("CORRELAÇÃO SPEARMAN")
print("=" * 60)

for ano in [
    2020,
    2021,
]:

    dados_ano = setorial[
        setorial["ano"] == ano
    ]

    corr = (
        dados_ano[
            variaveis_correlacao
        ]
        .corr(
            method="spearman"
        )
    )

    print(f"\nANO {ano}")

    print(
        corr[
            "saldo_por_1000_hab"
        ]
        .sort_values(
            ascending=False
        )
    )


# ============================================================
# 10. EMPREGO POR SETOR DOMINANTE
# ============================================================

resumo_setor = (
    setorial
    .groupby(
        [
            "ano",
            "setor_dominante",
        ]
    )
    .agg(
        municipios=(
            "codigo_ibge",
            "count"
        ),

        saldo_medio=(
            "saldo_empregos",
            "mean"
        ),

        saldo_mediano=(
            "saldo_empregos",
            "median"
        ),

        saldo_1000_medio=(
            "saldo_por_1000_hab",
            "mean"
        ),

        saldo_1000_mediano=(
            "saldo_por_1000_hab",
            "median"
        ),

        pib_per_capita_mediano=(
            "pib_per_capita",
            "median"
        ),
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("EMPREGO POR SETOR DOMINANTE")
print("=" * 60)

print(
    resumo_setor
    .round(2)
    .to_string(
        index=False
    )
)


# ============================================================
# 11. MUDANÇA 2020 → 2021
# ============================================================

base_2020 = setorial[
    setorial["ano"] == 2020
][
    [
        "codigo_ibge",
        "municipio",
        "setor_dominante",
        "saldo_por_1000_hab",
        "participacao_agro_pct",
        "participacao_industria_pct",
        "participacao_servicos_pct",
        "participacao_adm_publica_pct",
    ]
].copy()


base_2021 = setorial[
    setorial["ano"] == 2021
][
    [
        "codigo_ibge",
        "saldo_por_1000_hab",
    ]
].copy()


comparacao = base_2020.merge(
    base_2021,
    on="codigo_ibge",
    how="inner",
    suffixes=(
        "_2020",
        "_2021"
    ),
    validate="one_to_one"
)


comparacao[
    "variacao_saldo_1000_2021"
] = (
    comparacao[
        "saldo_por_1000_hab_2021"
    ]
    - comparacao[
        "saldo_por_1000_hab_2020"
    ]
)


# ============================================================
# 12. RECUPERAÇÃO POR SETOR
# ============================================================

recuperacao_setor = (
    comparacao
    .groupby(
        "setor_dominante"
    )
    .agg(
        municipios=(
            "codigo_ibge",
            "count"
        ),

        variacao_media=(
            "variacao_saldo_1000_2021",
            "mean"
        ),

        variacao_mediana=(
            "variacao_saldo_1000_2021",
            "median"
        ),
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("VARIAÇÃO DO SALDO/1000 - 2020 → 2021")
print("=" * 60)

print(
    recuperacao_setor
    .round(2)
    .to_string(
        index=False
    )
)


# ============================================================
# 13. CORRELAÇÃO DA ESTRUTURA DE 2020 COM A MUDANÇA EM 2021
# ============================================================

print("\n" + "=" * 60)
print("ESTRUTURA 2020 × VARIAÇÃO DO EMPREGO EM 2021")
print("=" * 60)

colunas_temporais = [
    "participacao_agro_pct",
    "participacao_industria_pct",
    "participacao_servicos_pct",
    "participacao_adm_publica_pct",
    "variacao_saldo_1000_2021",
]


print(
    comparacao[
        colunas_temporais
    ]
    .corr(
        method="spearman"
    )[
        "variacao_saldo_1000_2021"
    ]
    .sort_values(
        ascending=False
    )
)


# ============================================================
# 14. MAIORES PARTICIPAÇÕES SETORIAIS
# ============================================================

for coluna, nome in mapa_setores.items():

    print("\n" + "=" * 60)
    print(
        f"MAIORES PARTICIPAÇÕES - {nome.upper()}"
    )
    print("=" * 60)

    print(
        setorial[
            setorial["ano"] == 2021
        ][
            [
                "municipio",
                coluna,
                "saldo_por_1000_hab",
                "pib_per_capita",
            ]
        ]
        .sort_values(
            coluna,
            ascending=False
        )
        .head(15)
        .round(2)
        .to_string(
            index=False
        )
    )


# ============================================================
# 15. SALVAMENTO
# ============================================================

setorial.to_csv(
    OUTPUT_DIR
    / "base_setorial_2020_2021.csv",
    index=False,
    encoding="utf-8-sig"
)


resumo_setor.to_csv(
    OUTPUT_DIR
    / "resumo_por_setor_dominante.csv",
    index=False,
    encoding="utf-8-sig"
)


comparacao.to_csv(
    OUTPUT_DIR
    / "comparacao_setorial_2020_2021.csv",
    index=False,
    encoding="utf-8-sig"
)


recuperacao_setor.to_csv(
    OUTPUT_DIR
    / "recuperacao_por_setor.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 16. FINAL
# ============================================================

print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)

print(
    OUTPUT_DIR
)

print(
    "\nAnálise setorial concluída com sucesso."
)