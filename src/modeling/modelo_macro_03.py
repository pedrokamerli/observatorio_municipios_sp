from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


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
    / "modelos"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(
    ARQUIVO
)


print("\n" + "=" * 60)
print("BASE NORMALIZADA")
print("=" * 60)

print("\nDimensão:")
print(df.shape)

print("\nAnos:")
print(
    sorted(
        df["ano"].unique()
    )
)


# ============================================================
# 3. FEATURES ADICIONAIS
# ============================================================

df[
    "razao_admissoes_desligamentos"
] = (
    df["admissoes"]
    / df["desligamentos"].replace(
        0,
        np.nan
    )
)


df[
    "saldo_sobre_movimentacoes"
] = (
    df["saldo_empregos"]
    / (
        df["admissoes"]
        + df["desligamentos"]
    ).replace(
        0,
        np.nan
    )
)


# ============================================================
# 4. FEATURES DO MODELO 03
# ============================================================

features = [

    # Economia
    "pib_per_capita",
    "crescimento_pib_pct",
    "crescimento_pib_per_capita_pct",

    # Mercado de trabalho normalizado
    "admissoes_por_1000_hab",
    "desligamentos_por_1000_hab",
    "saldo_por_1000_hab",
    "movimentacoes_por_1000_hab",

    # Histórico normalizado
    "saldo_por_1000_ano_anterior",
    "admissoes_por_1000_ano_anterior",
    "desligamentos_por_1000_ano_anterior",

    # Relações internas
    "razao_admissoes_desligamentos",
    "saldo_sobre_movimentacoes",
]


target = (
    "variacao_saldo_por_1000_proximo_ano"
)


# ============================================================
# 5. BASE DE MODELAGEM
# ============================================================

# IMPORTANTE:
# saldo_por_1000_hab NÃO aparece aqui explicitamente,
# porque ele já está dentro de "features".

colunas = [
    "ano",
    "codigo_ibge",
    "municipio",
    "populacao_2022",
    "saldo_empregos",
    "saldo_por_1000_proximo_ano",
    target,
    *features,
]


dados_ml = df[
    colunas
].copy()


# ============================================================
# 6. VERIFICAÇÃO DE COLUNAS DUPLICADAS
# ============================================================

duplicadas = (
    dados_ml.columns[
        dados_ml.columns.duplicated()
    ]
    .tolist()
)


print("\nColunas duplicadas:")
print(
    duplicadas
)


if duplicadas:

    raise ValueError(
        "Existem colunas duplicadas."
    )


# ============================================================
# 7. REMOVE REGISTROS INCOMPLETOS
# ============================================================

dados_ml = dados_ml.dropna(
    subset=[
        *features,
        target,
    ]
).copy()


print("\n" + "=" * 60)
print("BASE DE MACHINE LEARNING - MODELO 03")
print("=" * 60)

print("\nDimensão:")
print(
    dados_ml.shape
)

print("\nRegistros por ano:")
print(
    dados_ml
    .groupby("ano")
    .size()
)

print("\nValores ausentes:")
print(
    dados_ml[
        features + [target]
    ]
    .isna()
    .sum()
)


# ============================================================
# 8. DIVISÃO TEMPORAL
# ============================================================

# 2021:
# usa informações de 2020 e 2021
# para prever a mudança até 2022.
#
# 2022:
# será usado como teste
# para prever a mudança até 2023.

treino = dados_ml[
    dados_ml["ano"] == 2021
].copy()


teste = dados_ml[
    dados_ml["ano"] == 2022
].copy()


print("\n" + "=" * 60)
print("DIVISÃO TEMPORAL")
print("=" * 60)

print("\nTreino:")
print(
    treino.shape
)

print("\nAno de treino:")
print(
    sorted(
        treino["ano"].unique()
    )
)

print("\nTeste:")
print(
    teste.shape
)

print("\nAno de teste:")
print(
    sorted(
        teste["ano"].unique()
    )
)


if len(treino) == 0:
    raise ValueError(
        "A base de treino ficou vazia."
    )


if len(teste) == 0:
    raise ValueError(
        "A base de teste ficou vazia."
    )


# ============================================================
# 9. X E Y
# ============================================================

X_train = treino[
    features
]

y_train = treino[
    target
]


X_test = teste[
    features
]

y_test = teste[
    target
]


# ============================================================
# 10. FUNÇÃO DE AVALIAÇÃO
# ============================================================

def avaliar_modelo(
    nome,
    y_real_delta,
    y_previsto_delta,
    saldo_atual_taxa,
    saldo_real_taxa,
    populacao,
):

    # --------------------------------------------------------
    # MÉTRICAS SOBRE A VARIAÇÃO DA TAXA
    # --------------------------------------------------------

    mae_delta = mean_absolute_error(
        y_real_delta,
        y_previsto_delta
    )

    rmse_delta = np.sqrt(
        mean_squared_error(
            y_real_delta,
            y_previsto_delta
        )
    )

    r2_delta = r2_score(
        y_real_delta,
        y_previsto_delta
    )


    # --------------------------------------------------------
    # RECONSTRUÇÃO DA TAXA FUTURA
    # --------------------------------------------------------

    taxa_prevista = (
        saldo_atual_taxa
        + y_previsto_delta
    )


    mae_taxa = mean_absolute_error(
        saldo_real_taxa,
        taxa_prevista
    )

    rmse_taxa = np.sqrt(
        mean_squared_error(
            saldo_real_taxa,
            taxa_prevista
        )
    )

    r2_taxa = r2_score(
        saldo_real_taxa,
        taxa_prevista
    )


    # --------------------------------------------------------
    # CONVERSÃO PARA SALDO ABSOLUTO
    # --------------------------------------------------------

    saldo_real_absoluto = (
        saldo_real_taxa
        * populacao
        / 1000
    )


    saldo_previsto_absoluto = (
        taxa_prevista
        * populacao
        / 1000
    )


    mae_absoluto = mean_absolute_error(
        saldo_real_absoluto,
        saldo_previsto_absoluto
    )

    rmse_absoluto = np.sqrt(
        mean_squared_error(
            saldo_real_absoluto,
            saldo_previsto_absoluto
        )
    )

    r2_absoluto = r2_score(
        saldo_real_absoluto,
        saldo_previsto_absoluto
    )


    # --------------------------------------------------------
    # IMPRESSÃO
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print(nome)
    print("=" * 60)

    print("\nVARIAÇÃO DA TAXA:")

    print(
        f"MAE:  {mae_delta:,.4f}"
    )

    print(
        f"RMSE: {rmse_delta:,.4f}"
    )

    print(
        f"R²:   {r2_delta:.4f}"
    )


    print("\nTAXA FUTURA:")

    print(
        f"MAE:  {mae_taxa:,.4f}"
    )

    print(
        f"RMSE: {rmse_taxa:,.4f}"
    )

    print(
        f"R²:   {r2_taxa:.4f}"
    )


    print("\nSALDO ABSOLUTO RECONSTRUÍDO:")

    print(
        f"MAE:  {mae_absoluto:,.2f}"
    )

    print(
        f"RMSE: {rmse_absoluto:,.2f}"
    )

    print(
        f"R²:   {r2_absoluto:.4f}"
    )


    return {

        "modelo":
            nome,

        "mae_delta_taxa":
            mae_delta,

        "rmse_delta_taxa":
            rmse_delta,

        "r2_delta_taxa":
            r2_delta,

        "mae_taxa_futura":
            mae_taxa,

        "rmse_taxa_futura":
            rmse_taxa,

        "r2_taxa_futura":
            r2_taxa,

        "mae_saldo_absoluto":
            mae_absoluto,

        "rmse_saldo_absoluto":
            rmse_absoluto,

        "r2_saldo_absoluto":
            r2_absoluto,
    }


# ============================================================
# 11. VETORES AUXILIARES
# ============================================================

saldo_atual_taxa = (
    teste[
        "saldo_por_1000_hab"
    ]
    .to_numpy(
        dtype=float
    )
)


saldo_real_taxa = (
    teste[
        "saldo_por_1000_proximo_ano"
    ]
    .to_numpy(
        dtype=float
    )
)


populacao_teste = (
    teste[
        "populacao_2022"
    ]
    .to_numpy(
        dtype=float
    )
)


# ============================================================
# 12. LISTA DE RESULTADOS
# ============================================================

resultados = []


# ============================================================
# 13. BASELINE
# ============================================================

# Baseline:
# nenhuma mudança esperada na taxa.
#
# delta previsto = 0
#
# portanto:
# taxa futura prevista = taxa atual

baseline_delta = np.zeros(
    len(teste)
)


resultados.append(

    avaliar_modelo(

        "Baseline - nenhuma mudança",

        y_test,

        baseline_delta,

        saldo_atual_taxa,

        saldo_real_taxa,

        populacao_teste,

    )

)


# ============================================================
# 14. REGRESSÃO LINEAR
# ============================================================

modelo_linear = Pipeline(

    steps=[

        (
            "scaler",
            StandardScaler()
        ),

        (
            "modelo",
            LinearRegression()
        ),

    ]

)


modelo_linear.fit(
    X_train,
    y_train
)


pred_linear = (
    modelo_linear.predict(
        X_test
    )
)


resultados.append(

    avaliar_modelo(

        "Regressão Linear",

        y_test,

        pred_linear,

        saldo_atual_taxa,

        saldo_real_taxa,

        populacao_teste,

    )

)


# ============================================================
# 15. RIDGE
# ============================================================

modelo_ridge = Pipeline(

    steps=[

        (
            "scaler",
            StandardScaler()
        ),

        (
            "modelo",
            Ridge(
                alpha=10.0
            )
        ),

    ]

)


modelo_ridge.fit(
    X_train,
    y_train
)


pred_ridge = (
    modelo_ridge.predict(
        X_test
    )
)


resultados.append(

    avaliar_modelo(

        "Ridge",

        y_test,

        pred_ridge,

        saldo_atual_taxa,

        saldo_real_taxa,

        populacao_teste,

    )

)


# ============================================================
# 16. RANDOM FOREST
# ============================================================

modelo_rf = RandomForestRegressor(

    n_estimators=500,

    max_depth=8,

    min_samples_leaf=3,

    random_state=42,

    n_jobs=-1,

)


modelo_rf.fit(
    X_train,
    y_train
)


pred_rf = (
    modelo_rf.predict(
        X_test
    )
)


resultados.append(

    avaliar_modelo(

        "Random Forest",

        y_test,

        pred_rf,

        saldo_atual_taxa,

        saldo_real_taxa,

        populacao_teste,

    )

)


# ============================================================
# 17. COMPARAÇÃO DOS MODELOS
# ============================================================

resultados_df = pd.DataFrame(
    resultados
)


resultados_df = (
    resultados_df
    .sort_values(
        "mae_saldo_absoluto"
    )
    .reset_index(
        drop=True
    )
)


print("\n" + "=" * 60)
print("COMPARAÇÃO - MODELO 03")
print("=" * 60)


print(
    resultados_df
    .to_string(
        index=False
    )
)


# ============================================================
# 18. IMPORTÂNCIA DAS VARIÁVEIS
# ============================================================

importancias = pd.DataFrame({

    "variavel":
        features,

    "importancia":
        modelo_rf.feature_importances_,

})


importancias = (
    importancias
    .sort_values(
        "importancia",
        ascending=False
    )
    .reset_index(
        drop=True
    )
)


print("\n" + "=" * 60)
print("IMPORTÂNCIA DAS VARIÁVEIS - RANDOM FOREST")
print("=" * 60)


print(
    importancias
    .to_string(
        index=False
    )
)


# ============================================================
# 19. PREVISÕES
# ============================================================

previsoes = teste[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "populacao_2022",
        "saldo_empregos",
        "saldo_por_1000_hab",
        "saldo_por_1000_proximo_ano",
        target,
    ]
].copy()


previsoes[
    "delta_baseline"
] = baseline_delta


previsoes[
    "delta_linear"
] = pred_linear


previsoes[
    "delta_ridge"
] = pred_ridge


previsoes[
    "delta_random_forest"
] = pred_rf


# ============================================================
# 20. TAXAS PREVISTAS
# ============================================================

previsoes[
    "taxa_prevista_baseline"
] = (
    previsoes[
        "saldo_por_1000_hab"
    ]
    + previsoes[
        "delta_baseline"
    ]
)


previsoes[
    "taxa_prevista_linear"
] = (
    previsoes[
        "saldo_por_1000_hab"
    ]
    + previsoes[
        "delta_linear"
    ]
)


previsoes[
    "taxa_prevista_ridge"
] = (
    previsoes[
        "saldo_por_1000_hab"
    ]
    + previsoes[
        "delta_ridge"
    ]
)


previsoes[
    "taxa_prevista_random_forest"
] = (
    previsoes[
        "saldo_por_1000_hab"
    ]
    + previsoes[
        "delta_random_forest"
    ]
)


# ============================================================
# 21. SALDO REAL DE 2023
# ============================================================

previsoes[
    "saldo_real_2023"
] = (

    previsoes[
        "saldo_por_1000_proximo_ano"
    ]

    * previsoes[
        "populacao_2022"
    ]

    / 1000

)


# ============================================================
# 22. SALDOS ABSOLUTOS PREVISTOS
# ============================================================

for modelo in [
    "baseline",
    "linear",
    "ridge",
    "random_forest",
]:

    previsoes[
        f"saldo_previsto_{modelo}"
    ] = (

        previsoes[
            f"taxa_prevista_{modelo}"
        ]

        * previsoes[
            "populacao_2022"
        ]

        / 1000

    )


# ============================================================
# 23. ERRO RANDOM FOREST
# ============================================================

previsoes[
    "erro_rf"
] = (

    previsoes[
        "saldo_real_2023"
    ]

    - previsoes[
        "saldo_previsto_random_forest"
    ]

)


previsoes[
    "erro_absoluto_rf"
] = (

    previsoes[
        "erro_rf"
    ]
    .abs()

)


print("\n" + "=" * 60)
print("MAIORES ERROS - RANDOM FOREST")
print("=" * 60)


print(

    previsoes[
        [
            "municipio",
            "saldo_empregos",
            "saldo_real_2023",
            "saldo_previsto_random_forest",
            "erro_rf",
            "erro_absoluto_rf",
        ]
    ]

    .sort_values(
        "erro_absoluto_rf",
        ascending=False
    )

    .head(20)

    .to_string(
        index=False
    )

)


# ============================================================
# 24. EXEMPLO - BAURU
# ============================================================

print("\n" + "=" * 60)
print("PREVISÃO - BAURU")
print("=" * 60)


print(

    previsoes[
        previsoes[
            "municipio"
        ]
        .str.lower()
        .eq("bauru")
    ][
        [
            "municipio",
            "saldo_empregos",
            "saldo_por_1000_hab",
            "saldo_por_1000_proximo_ano",
            "saldo_real_2023",
            "saldo_previsto_baseline",
            "saldo_previsto_linear",
            "saldo_previsto_ridge",
            "saldo_previsto_random_forest",
        ]
    ]
    .to_string(
        index=False
    )

)


# ============================================================
# 25. SALVAMENTO
# ============================================================

ARQUIVO_RESULTADOS = (
    OUTPUT_DIR
    / "comparacao_modelos_macro_03.csv"
)


ARQUIVO_PREVISOES = (
    OUTPUT_DIR
    / "previsoes_2023_macro_03.csv"
)


ARQUIVO_IMPORTANCIAS = (
    OUTPUT_DIR
    / "importancia_variaveis_rf_macro_03.csv"
)


resultados_df.to_csv(

    ARQUIVO_RESULTADOS,

    index=False,

    encoding="utf-8-sig"

)


previsoes.to_csv(

    ARQUIVO_PREVISOES,

    index=False,

    encoding="utf-8-sig"

)


importancias.to_csv(

    ARQUIVO_IMPORTANCIAS,

    index=False,

    encoding="utf-8-sig"

)


# ============================================================
# 26. FINAL
# ============================================================

print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)


print(
    ARQUIVO_RESULTADOS
)

print(
    ARQUIVO_PREVISOES
)

print(
    ARQUIVO_IMPORTANCIAS
)


print(
    "\nModelo Macro 03 concluído com sucesso."
)