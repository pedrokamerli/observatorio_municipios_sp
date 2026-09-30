from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARQUIVO_PREVISOES = (
    PROJECT_ROOT
    / "outputs"
    / "modelos"
    / "previsoes_2023_macro_03.csv"
)

ARQUIVO_PAINEL = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "base_painel_normalizado_sp_2020_2023.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "analise_residuos"
    / "modelo03"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA
# ============================================================

previsoes = pd.read_csv(
    ARQUIVO_PREVISOES
)

painel = pd.read_csv(
    ARQUIVO_PAINEL
)


print("\n" + "=" * 60)
print("BASES CARREGADAS")
print("=" * 60)

print("\nPrevisões:")
print(
    previsoes.shape
)

print("\nPainel:")
print(
    painel.shape
)


# ============================================================
# 3. DADOS ECONÔMICOS DE 2022
# ============================================================

economia_2022 = painel[
    painel["ano"] == 2022
][
    [
        "codigo_ibge",
        "pib",
        "pib_per_capita",
        "populacao_2022",
    ]
].copy()


print("\nEconomia 2022:")
print(
    economia_2022.shape
)


print("\nMunicípios únicos:")
print(
    economia_2022[
        "codigo_ibge"
    ].nunique()
)


# ============================================================
# 4. MERGE
# ============================================================

df = previsoes.merge(
    economia_2022[
        [
            "codigo_ibge",
            "pib",
            "pib_per_capita",
        ]
    ],
    on="codigo_ibge",
    how="left",
    validate="one_to_one",
    indicator=True
)


print("\n" + "=" * 60)
print("VALIDAÇÃO DO MERGE")
print("=" * 60)

print(
    df["_merge"]
    .value_counts()
)


if df["_merge"].ne("both").any():

    raise ValueError(
        "Existem municípios sem correspondência."
    )


df = df.drop(
    columns="_merge"
)


# ============================================================
# 5. RESÍDUOS
# ============================================================

# Residual:
#
# real - previsto
#
# positivo:
# modelo PREVIU MENOS do que aconteceu
#
# negativo:
# modelo PREVIU MAIS do que aconteceu

df["residuo"] = (
    df["saldo_real_2023"]
    - df["saldo_previsto_random_forest"]
)


df["erro_absoluto"] = (
    df["residuo"]
    .abs()
)


df["erro_quadratico"] = (
    df["residuo"] ** 2
)


# ============================================================
# 6. VALIDAÇÃO
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DOS RESÍDUOS")
print("=" * 60)

print("\nDimensão:")
print(
    df.shape
)

print("\nValores ausentes:")
print(
    df[
        [
            "saldo_real_2023",
            "saldo_previsto_random_forest",
            "residuo",
            "erro_absoluto",
            "populacao_2022",
            "pib_per_capita",
        ]
    ]
    .isna()
    .sum()
)


# ============================================================
# 7. MÉTRICAS GERAIS
# ============================================================

y_real = df[
    "saldo_real_2023"
]

y_pred = df[
    "saldo_previsto_random_forest"
]


mae = mean_absolute_error(
    y_real,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_real,
        y_pred
    )
)

r2 = r2_score(
    y_real,
    y_pred
)

bias = (
    df["residuo"]
    .mean()
)

mediana_residuo = (
    df["residuo"]
    .median()
)

mediana_erro_absoluto = (
    df["erro_absoluto"]
    .median()
)


print("\n" + "=" * 60)
print("MÉTRICAS GERAIS - MODELO 03 RANDOM FOREST")
print("=" * 60)

print(
    f"MAE: {mae:,.2f}"
)

print(
    f"RMSE: {rmse:,.2f}"
)

print(
    f"R²: {r2:.4f}"
)

print(
    f"Bias médio: {bias:,.2f}"
)

print(
    f"Mediana do resíduo: "
    f"{mediana_residuo:,.2f}"
)

print(
    f"Mediana do erro absoluto: "
    f"{mediana_erro_absoluto:,.2f}"
)


# ============================================================
# 8. DISTRIBUIÇÃO DOS RESÍDUOS
# ============================================================

print("\n" + "=" * 60)
print("DISTRIBUIÇÃO DOS RESÍDUOS")
print("=" * 60)

print(
    df["residuo"]
    .describe(
        percentiles=[
            0.01,
            0.05,
            0.10,
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99,
        ]
    )
)


# ============================================================
# 9. SUPER / SUBESTIMAÇÃO
# ============================================================

df["tipo_erro"] = np.select(
    [
        df["residuo"] > 0,
        df["residuo"] < 0,
    ],
    [
        "Modelo subestimou",
        "Modelo superestimou",
    ],
    default="Previsão exata"
)


print("\n" + "=" * 60)
print("DIREÇÃO DOS ERROS")
print("=" * 60)

print(
    df["tipo_erro"]
    .value_counts()
)


print("\nPercentual:")

print(
    (
        df["tipo_erro"]
        .value_counts(
            normalize=True
        )
        * 100
    )
    .round(2)
)


# ============================================================
# 10. FAIXAS DE POPULAÇÃO
# ============================================================

faixas_populacao = [
    0,
    10_000,
    50_000,
    100_000,
    500_000,
    np.inf,
]

rotulos_populacao = [
    "Até 10 mil",
    "10 a 50 mil",
    "50 a 100 mil",
    "100 a 500 mil",
    "Acima de 500 mil",
]


df["porte_populacional"] = pd.cut(
    df["populacao_2022"],
    bins=faixas_populacao,
    labels=rotulos_populacao,
    right=False,
)


# ============================================================
# 11. FUNÇÃO PARA MÉTRICAS POR GRUPO
# ============================================================

def metricas_grupo(grupo):

    real = grupo[
        "saldo_real_2023"
    ]

    previsto = grupo[
        "saldo_previsto_random_forest"
    ]

    return pd.Series({

        "municipios":
            len(grupo),

        "mae":
            mean_absolute_error(
                real,
                previsto
            ),

        "rmse":
            np.sqrt(
                mean_squared_error(
                    real,
                    previsto
                )
            ),

        "bias":
            grupo[
                "residuo"
            ].mean(),

        "mediana_erro_abs":
            grupo[
                "erro_absoluto"
            ].median(),

        "r2":
            (
                r2_score(
                    real,
                    previsto
                )
                if len(grupo) > 1
                else np.nan
            ),

    })


# ============================================================
# 12. ERRO POR PORTE POPULACIONAL
# ============================================================

erro_por_porte = (
    df.groupby(
        "porte_populacional",
        observed=False
    )
    .apply(
        metricas_grupo,
        include_groups=False
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("ERRO POR PORTE POPULACIONAL")
print("=" * 60)

print(
    erro_por_porte
    .to_string(
        index=False
    )
)


# ============================================================
# 13. QUARTIS DE PIB PER CAPITA
# ============================================================

df["faixa_pib_per_capita"] = pd.qcut(
    df["pib_per_capita"],
    q=4,
    labels=[
        "Q1 - menor",
        "Q2",
        "Q3",
        "Q4 - maior",
    ]
)


erro_por_pib = (
    df.groupby(
        "faixa_pib_per_capita",
        observed=False
    )
    .apply(
        metricas_grupo,
        include_groups=False
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("ERRO POR FAIXA DE PIB PER CAPITA")
print("=" * 60)

print(
    erro_por_pib
    .to_string(
        index=False
    )
)


# ============================================================
# 14. MUNICÍPIOS COM SALDO POSITIVO / NEGATIVO
# ============================================================

df["situacao_real_2023"] = np.select(
    [
        df["saldo_real_2023"] > 0,
        df["saldo_real_2023"] < 0,
    ],
    [
        "Saldo positivo",
        "Saldo negativo",
    ],
    default="Saldo zero"
)


erro_por_situacao = (
    df.groupby(
        "situacao_real_2023"
    )
    .apply(
        metricas_grupo,
        include_groups=False
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("ERRO POR SITUAÇÃO REAL DE 2023")
print("=" * 60)

print(
    erro_por_situacao
    .to_string(
        index=False
    )
)


# ============================================================
# 15. MAIORES ERROS ABSOLUTOS
# ============================================================

maiores_erros = (
    df[
        [
            "municipio",
            "populacao_2022",
            "pib_per_capita",
            "saldo_real_2023",
            "saldo_previsto_random_forest",
            "residuo",
            "erro_absoluto",
        ]
    ]
    .sort_values(
        "erro_absoluto",
        ascending=False
    )
    .head(25)
)


print("\n" + "=" * 60)
print("25 MAIORES ERROS ABSOLUTOS")
print("=" * 60)

print(
    maiores_erros
    .to_string(
        index=False
    )
)


# ============================================================
# 16. MAIORES SUBESTIMAÇÕES
# ============================================================

subestimados = (
    df[
        [
            "municipio",
            "saldo_real_2023",
            "saldo_previsto_random_forest",
            "residuo",
        ]
    ]
    .sort_values(
        "residuo",
        ascending=False
    )
    .head(20)
)


print("\n" + "=" * 60)
print("MAIORES SUBESTIMAÇÕES")
print("=" * 60)

print(
    subestimados
    .to_string(
        index=False
    )
)


# ============================================================
# 17. MAIORES SUPERESTIMAÇÕES
# ============================================================

superestimados = (
    df[
        [
            "municipio",
            "saldo_real_2023",
            "saldo_previsto_random_forest",
            "residuo",
        ]
    ]
    .sort_values(
        "residuo",
        ascending=True
    )
    .head(20)
)


print("\n" + "=" * 60)
print("MAIORES SUPERESTIMAÇÕES")
print("=" * 60)

print(
    superestimados
    .to_string(
        index=False
    )
)


# ============================================================
# 18. CORRELAÇÃO ENTRE ERRO E ESCALA
# ============================================================

correlacao_pop = (
    df[
        [
            "erro_absoluto",
            "populacao_2022",
        ]
    ]
    .corr(
        method="spearman"
    )
    .iloc[0, 1]
)


correlacao_pib = (
    df[
        [
            "erro_absoluto",
            "pib_per_capita",
        ]
    ]
    .corr(
        method="spearman"
    )
    .iloc[0, 1]
)


print("\n" + "=" * 60)
print("ERRO × CARACTERÍSTICAS MUNICIPAIS")
print("=" * 60)

print(
    "Spearman erro absoluto × população:"
)

print(
    round(
        correlacao_pop,
        4
    )
)


print(
    "\nSpearman erro absoluto × PIB per capita:"
)

print(
    round(
        correlacao_pib,
        4
    )
)


# ============================================================
# 19. GRÁFICO - REAL X PREVISTO
# ============================================================

plt.figure(
    figsize=(9, 7)
)

plt.scatter(
    df["saldo_real_2023"],
    df["saldo_previsto_random_forest"],
    alpha=0.6
)


minimo = min(
    df["saldo_real_2023"].min(),
    df["saldo_previsto_random_forest"].min()
)

maximo = max(
    df["saldo_real_2023"].max(),
    df["saldo_previsto_random_forest"].max()
)


plt.plot(
    [
        minimo,
        maximo,
    ],
    [
        minimo,
        maximo,
    ],
    linestyle="--"
)


plt.xlabel(
    "Saldo real de empregos - 2023"
)

plt.ylabel(
    "Saldo previsto - Random Forest"
)

plt.title(
    "Saldo real × saldo previsto - Modelo Macro 03"
)

plt.tight_layout()


plt.savefig(
    OUTPUT_DIR
    / "01_real_vs_previsto.png",
    dpi=300
)

plt.close()


# ============================================================
# 20. GRÁFICO - DISTRIBUIÇÃO DOS RESÍDUOS
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.hist(
    df["residuo"],
    bins=50
)

plt.axvline(
    0,
    linestyle="--"
)

plt.xlabel(
    "Resíduo (real - previsto)"
)

plt.ylabel(
    "Número de municípios"
)

plt.title(
    "Distribuição dos resíduos - Modelo Macro 03"
)

plt.tight_layout()


plt.savefig(
    OUTPUT_DIR
    / "02_distribuicao_residuos.png",
    dpi=300
)

plt.close()


# ============================================================
# 21. GRÁFICO - ERRO X POPULAÇÃO
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.scatter(
    np.log1p(
        df["populacao_2022"]
    ),
    df["erro_absoluto"],
    alpha=0.6
)

plt.xlabel(
    "log(População - Censo 2022)"
)

plt.ylabel(
    "Erro absoluto"
)

plt.title(
    "Erro absoluto × porte populacional"
)

plt.tight_layout()


plt.savefig(
    OUTPUT_DIR
    / "03_erro_vs_populacao.png",
    dpi=300
)

plt.close()


# ============================================================
# 22. GRÁFICO - RESÍDUOS POR PORTE
# ============================================================

dados_boxplot = []

rotulos_boxplot = []


for categoria in rotulos_populacao:

    valores = (
        df[
            df[
                "porte_populacional"
            ]
            == categoria
        ][
            "residuo"
        ]
        .dropna()
        .values
    )

    dados_boxplot.append(
        valores
    )

    rotulos_boxplot.append(
        categoria
    )


plt.figure(
    figsize=(11, 7)
)

plt.boxplot(
    dados_boxplot,
    tick_labels=rotulos_boxplot,
    showfliers=True
)

plt.axhline(
    0,
    linestyle="--"
)

plt.xlabel(
    "Porte populacional"
)

plt.ylabel(
    "Resíduo (real - previsto)"
)

plt.title(
    "Distribuição dos resíduos por porte municipal"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()


plt.savefig(
    OUTPUT_DIR
    / "04_residuos_por_porte.png",
    dpi=300
)

plt.close()


# ============================================================
# 23. GRÁFICO - MAE POR PORTE
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.bar(
    erro_por_porte[
        "porte_populacional"
    ].astype(str),
    erro_por_porte[
        "mae"
    ]
)

plt.xlabel(
    "Porte populacional"
)

plt.ylabel(
    "MAE"
)

plt.title(
    "Erro absoluto médio por porte municipal"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()


plt.savefig(
    OUTPUT_DIR
    / "05_mae_por_porte.png",
    dpi=300
)

plt.close()


# ============================================================
# 24. SALVAMENTO DAS TABELAS
# ============================================================

df.to_csv(
    OUTPUT_DIR
    / "residuos_modelo03.csv",
    index=False,
    encoding="utf-8-sig"
)


erro_por_porte.to_csv(
    OUTPUT_DIR
    / "erro_por_porte.csv",
    index=False,
    encoding="utf-8-sig"
)


erro_por_pib.to_csv(
    OUTPUT_DIR
    / "erro_por_pib_per_capita.csv",
    index=False,
    encoding="utf-8-sig"
)


erro_por_situacao.to_csv(
    OUTPUT_DIR
    / "erro_por_situacao_2023.csv",
    index=False,
    encoding="utf-8-sig"
)


maiores_erros.to_csv(
    OUTPUT_DIR
    / "maiores_erros.csv",
    index=False,
    encoding="utf-8-sig"
)


subestimados.to_csv(
    OUTPUT_DIR
    / "maiores_subestimacoes.csv",
    index=False,
    encoding="utf-8-sig"
)


superestimados.to_csv(
    OUTPUT_DIR
    / "maiores_superestimacoes.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 25. FINAL
# ============================================================

print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)

print(
    OUTPUT_DIR
)

print("\nGráficos:")

for arquivo in sorted(
    OUTPUT_DIR.glob("*.png")
):

    print(
        arquivo.name
    )


print(
    "\nAnálise de resíduos concluída com sucesso."
)