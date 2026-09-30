from pathlib import Path

import numpy as np
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

MODELOS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "modelos"
)

PAINEL_FILE = (
    PROCESSED_DIR
    / "base_painel_normalizado_sp_2020_2023.csv"
)

POP_REFERENCIA_FILE = (
    PROCESSED_DIR
    / "populacao_referencia_sp_2020_2023.csv"
)

PREVISOES_FILE = (
    MODELOS_DIR
    / "previsoes_2023_macro_03.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "base_observatorio_sp.csv"
)


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(
    PAINEL_FILE
)

pop_ref = pd.read_csv(
    POP_REFERENCIA_FILE
)

previsoes = pd.read_csv(
    PREVISOES_FILE
)


print("\n" + "=" * 70)
print("BASES CARREGADAS")
print("=" * 70)

print("\nPainel:")
print(df.shape)

print("\nPopulação de referência:")
print(pop_ref.shape)

print("\nPrevisões:")
print(previsoes.shape)


# ============================================================
# 3. POPULAÇÃO DE REFERÊNCIA
# ============================================================

pop_ref = pop_ref[
    [
        "ano",
        "codigo_ibge",
        "populacao_referencia",
        "ano_referencia_populacao",
        "tipo_populacao",
    ]
].copy()


df = df.merge(
    pop_ref,
    on=[
        "ano",
        "codigo_ibge",
    ],
    how="left",
    validate="one_to_one",
)


# ============================================================
# 4. PORTE MUNICIPAL
# ============================================================

faixas = [
    0,
    10_000,
    50_000,
    100_000,
    500_000,
    np.inf,
]

rotulos = [
    "Até 10 mil",
    "10 a 50 mil",
    "50 a 100 mil",
    "100 a 500 mil",
    "Acima de 500 mil",
]


df["porte_municipal"] = pd.cut(
    df["populacao_2022"],
    bins=faixas,
    labels=rotulos,
    right=False,
)


# ============================================================
# 5. PARTICIPAÇÃO ECONÔMICA
# ============================================================

# Recalcula somente quando VAB estiver disponível.

df["participacao_agro_pct"] = (
    df["vab_agropecuaria"]
    / df["pib"]
    * 100
)

df["participacao_industria_pct"] = (
    df["vab_industria"]
    / df["pib"]
    * 100
)

df["participacao_servicos_pct"] = (
    df["vab_servicos"]
    / df["pib"]
    * 100
)

df["participacao_adm_publica_pct"] = (
    df["vab_administracao_publica"]
    / df["pib"]
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


colunas_setoriais = list(
    mapa_setores.keys()
)


tem_vab = (
    df[
        colunas_setoriais
    ]
    .notna()
    .any(axis=1)
)


df["setor_dominante"] = pd.NA


df.loc[
    tem_vab,
    "setor_dominante"
] = (
    df.loc[
        tem_vab,
        colunas_setoriais
    ]
    .idxmax(axis=1)
    .map(mapa_setores)
)


# ============================================================
# 7. VARIAÇÕES ANUAIS
# ============================================================

df = df.sort_values(
    [
        "codigo_ibge",
        "ano",
    ]
).reset_index(
    drop=True
)


df["variacao_saldo_empregos"] = (
    df.groupby(
        "codigo_ibge"
    )[
        "saldo_empregos"
    ]
    .diff()
)


df[
    "variacao_saldo_1000"
] = (
    df.groupby(
        "codigo_ibge"
    )[
        "saldo_por_1000_hab"
    ]
    .diff()
)


# ============================================================
# 8. RANKINGS POR ANO
# ============================================================

df[
    "ranking_pib"
] = (
    df.groupby("ano")[
        "pib"
    ]
    .rank(
        method="min",
        ascending=False
    )
    .astype("int64")
)


df[
    "ranking_pib_per_capita"
] = (
    df.groupby("ano")[
        "pib_per_capita"
    ]
    .rank(
        method="min",
        ascending=False
    )
    .astype("int64")
)


df[
    "ranking_saldo_empregos"
] = (
    df.groupby("ano")[
        "saldo_empregos"
    ]
    .rank(
        method="min",
        ascending=False
    )
    .astype("int64")
)


df[
    "ranking_saldo_1000"
] = (
    df.groupby("ano")[
        "saldo_por_1000_hab"
    ]
    .rank(
        method="min",
        ascending=False
    )
    .astype("int64")
)


# ============================================================
# 9. PREVISÕES DO MODELO 03
# ============================================================

previsoes_modelo = previsoes[
    [
        "codigo_ibge",
        "saldo_real_2023",
        "saldo_previsto_random_forest",
        "erro_rf",
        "erro_absoluto_rf",
    ]
].copy()


previsoes_modelo = previsoes_modelo.rename(
    columns={
        "saldo_previsto_random_forest":
            "modelo03_saldo_previsto",

        "erro_rf":
            "modelo03_residuo",

        "erro_absoluto_rf":
            "modelo03_erro_absoluto",
    }
)


# ============================================================
# 10. MERGE DAS PREVISÕES SOMENTE EM 2023
# ============================================================

df = df.merge(
    previsoes_modelo,
    on="codigo_ibge",
    how="left",
    validate="many_to_one",
)


# Como a previsão se refere somente a 2023,
# apagamos os valores nas linhas de outros anos.

colunas_previsao = [
    "saldo_real_2023",
    "modelo03_saldo_previsto",
    "modelo03_residuo",
    "modelo03_erro_absoluto",
]


df.loc[
    df["ano"] != 2023,
    colunas_previsao
] = np.nan


# ============================================================
# 11. DIREÇÃO DO ERRO DO MODELO
# ============================================================

df[
    "modelo03_tipo_erro"
] = pd.NA


df.loc[
    (
        df["ano"] == 2023
    )
    &
    (
        df["modelo03_residuo"] > 0
    ),
    "modelo03_tipo_erro"
] = "Modelo subestimou"


df.loc[
    (
        df["ano"] == 2023
    )
    &
    (
        df["modelo03_residuo"] < 0
    ),
    "modelo03_tipo_erro"
] = "Modelo superestimou"


df.loc[
    (
        df["ano"] == 2023
    )
    &
    (
        df["modelo03_residuo"] == 0
    ),
    "modelo03_tipo_erro"
] = "Previsão exata"


# ============================================================
# 12. VALIDAÇÕES
# ============================================================

print("\n" + "=" * 70)
print("VALIDAÇÃO DA BASE DO OBSERVATÓRIO")
print("=" * 70)

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


if len(df) != 2580:

    raise ValueError(
        f"Esperadas 2580 linhas. "
        f"Encontradas: {len(df)}"
    )


if duplicidades != 0:

    raise ValueError(
        "Existem duplicidades município + ano."
    )


# ============================================================
# 13. VALIDAÇÃO DAS PREVISÕES
# ============================================================

previsoes_2023 = df[
    df["ano"] == 2023
][
    "modelo03_saldo_previsto"
]


print("\nPrevisões Modelo 03 em 2023:")
print(
    previsoes_2023.notna().sum()
)


if (
    previsoes_2023
    .notna()
    .sum()
    != 645
):

    raise ValueError(
        "Esperadas 645 previsões para 2023."
    )


# ============================================================
# 14. EXEMPLO BAURU
# ============================================================

print("\n" + "=" * 70)
print("OBSERVATÓRIO - BAURU")
print("=" * 70)

colunas_bauru = [
    "ano",
    "municipio",
    "populacao_referencia",
    "pib",
    "pib_per_capita",
    "saldo_empregos",
    "saldo_por_1000_hab",
    "ranking_pib",
    "ranking_pib_per_capita",
    "ranking_saldo_empregos",
    "ranking_saldo_1000",
    "setor_dominante",
    "modelo03_saldo_previsto",
    "modelo03_residuo",
]


print(
    df[
        df["municipio"]
        .str.lower()
        .eq("bauru")
    ][
        colunas_bauru
    ]
    .round(2)
    .to_string(
        index=False
    )
)


# ============================================================
# 15. COLUNAS FINAIS IMPORTANTES
# ============================================================

print("\n" + "=" * 70)
print("COLUNAS DISPONÍVEIS")
print("=" * 70)

for coluna in df.columns:

    print(
        coluna
    )


# ============================================================
# 16. SALVAMENTO
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 70)
print("ARQUIVO GERADO")
print("=" * 70)

print(
    OUTPUT_FILE
)

print("\nExiste?")
print(
    OUTPUT_FILE.exists()
)


print(
    "\nBase final do Observatório criada com sucesso."
)