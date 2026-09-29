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
    / "base_painel_sp_2020_2023.csv"
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

df = pd.read_csv(ARQUIVO)

print("\n" + "=" * 60)
print("BASE CARREGADA")
print("=" * 60)

print("\nDimensão:")
print(df.shape)

print("\nAnos:")
print(sorted(df["ano"].unique()))


# ============================================================
# 3. NOVO TARGET
# ============================================================

# Em vez de prever diretamente o saldo futuro,
# vamos prever quanto o saldo muda de um ano para o outro.

df["variacao_saldo_proximo_ano"] = (
    df["saldo_empregos_proximo_ano"]
    - df["saldo_empregos"]
)


# ============================================================
# 4. FEATURE ENGINEERING
# ============================================================

df["razao_admissoes_desligamentos"] = (
    df["admissoes"]
    / df["desligamentos"].replace(0, np.nan)
)

df["movimentacoes_total"] = (
    df["admissoes"]
    + df["desligamentos"]
)

df["saldo_sobre_movimentacoes"] = (
    df["saldo_empregos"]
    / df["movimentacoes_total"].replace(0, np.nan)
)


# ============================================================
# 5. FEATURES
# ============================================================

features = [
    "pib",
    "pib_per_capita",
    "crescimento_pib_pct",
    "crescimento_pib_per_capita_pct",
    "admissoes",
    "desligamentos",
    "saldo_empregos",
    "saldo_empregos_ano_anterior",
    "admissoes_ano_anterior",
    "desligamentos_ano_anterior",
    "razao_admissoes_desligamentos",
    "movimentacoes_total",
    "saldo_sobre_movimentacoes",
]

target = "variacao_saldo_proximo_ano"


# ============================================================
# 6. BASE PARA MODELAGEM
# ============================================================

colunas_modelagem = [
    "ano",
    "codigo_ibge",
    "municipio",
    "saldo_empregos_proximo_ano",
    target,
    *features,
]

dados_ml = df[
    colunas_modelagem
].copy()


# Remove registros sem lag, crescimento ou target.
# Na prática, 2020 não possui ano anterior
# e 2023 não possui target futuro.

dados_ml = dados_ml.dropna(
    subset=[
        *features,
        target,
    ]
).copy()

print("\nColunas duplicadas:")
print(
    dados_ml.columns[
        dados_ml.columns.duplicated()
    ].tolist()
)

if dados_ml.columns.duplicated().any():
    raise ValueError(
        "Existem colunas duplicadas na base de modelagem."
    )

print("\n" + "=" * 60)
print("BASE DE MACHINE LEARNING - MODELO 02")
print("=" * 60)

print("\nDimensão:")
print(dados_ml.shape)

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
# 7. DIVISÃO TEMPORAL
# ============================================================

# 2021:
# usa informações de 2020/2021
# para prever 2022
#
# 2022:
# será nosso teste para prever 2023

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
print(treino.shape)

print("\nAno de treino:")
print(sorted(treino["ano"].unique()))

print("\nTeste:")
print(teste.shape)

print("\nAno de teste:")
print(sorted(teste["ano"].unique()))


if len(treino) == 0:
    raise ValueError(
        "A base de treino ficou vazia."
    )

if len(teste) == 0:
    raise ValueError(
        "A base de teste ficou vazia."
    )


# ============================================================
# 8. X E Y
# ============================================================

X_train = treino[features]
y_train = treino[target]

X_test = teste[features]
y_test = teste[target]


# ============================================================
# 9. FUNÇÃO DE AVALIAÇÃO
# ============================================================

def avaliar_modelo(
    nome,
    y_real_delta,
    y_previsto_delta,
    saldo_atual,
    saldo_real_futuro,
):

    # Métricas sobre a mudança prevista
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

    # Reconstrói o saldo futuro:
    #
    # saldo futuro previsto =
    # saldo atual + mudança prevista

    saldo_previsto_futuro = (
        saldo_atual
        + y_previsto_delta
    )

    mae_saldo = mean_absolute_error(
        saldo_real_futuro,
        saldo_previsto_futuro
    )

    rmse_saldo = np.sqrt(
        mean_squared_error(
            saldo_real_futuro,
            saldo_previsto_futuro
        )
    )

    r2_saldo = r2_score(
        saldo_real_futuro,
        saldo_previsto_futuro
    )

    print("\n" + "=" * 60)
    print(nome)
    print("=" * 60)

    print("\nMétricas da VARIAÇÃO:")

    print(
        f"MAE:  {mae_delta:,.2f}"
    )

    print(
        f"RMSE: {rmse_delta:,.2f}"
    )

    print(
        f"R²:   {r2_delta:.4f}"
    )

    print("\nMétricas do SALDO FUTURO reconstruído:")

    print(
        f"MAE:  {mae_saldo:,.2f}"
    )

    print(
        f"RMSE: {rmse_saldo:,.2f}"
    )

    print(
        f"R²:   {r2_saldo:.4f}"
    )

    return {
        "modelo": nome,
        "mae_delta": mae_delta,
        "rmse_delta": rmse_delta,
        "r2_delta": r2_delta,
        "mae_saldo_futuro": mae_saldo,
        "rmse_saldo_futuro": rmse_saldo,
        "r2_saldo_futuro": r2_saldo,
    }


# ============================================================
# 10. VALORES AUXILIARES
# ============================================================

saldo_atual_teste = (
    teste["saldo_empregos"]
    .to_numpy()
)

saldo_real_futuro = (
    teste["saldo_empregos_proximo_ano"]
    .to_numpy()
)


# ============================================================
# 11. BASELINE
# ============================================================

# Baseline:
# assume que não haverá mudança.
#
# delta previsto = 0
#
# Portanto:
# saldo futuro previsto = saldo atual

baseline_delta = np.zeros(
    len(teste)
)

resultados = []

resultados.append(
    avaliar_modelo(
        "Baseline - nenhuma mudança",
        y_test,
        baseline_delta,
        saldo_atual_teste,
        saldo_real_futuro,
    )
)


# ============================================================
# 12. REGRESSÃO LINEAR
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
        saldo_atual_teste,
        saldo_real_futuro,
    )
)


# ============================================================
# 13. RIDGE
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
        saldo_atual_teste,
        saldo_real_futuro,
    )
)


# ============================================================
# 14. RANDOM FOREST
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
        saldo_atual_teste,
        saldo_real_futuro,
    )
)


# ============================================================
# 15. COMPARAÇÃO
# ============================================================

resultados_df = pd.DataFrame(
    resultados
)

resultados_df = (
    resultados_df
    .sort_values(
        "mae_saldo_futuro"
    )
    .reset_index(
        drop=True
    )
)


print("\n" + "=" * 60)
print("COMPARAÇÃO DOS MODELOS")
print("=" * 60)

print(
    resultados_df
    .to_string(
        index=False
    )
)


# ============================================================
# 16. FEATURE IMPORTANCE
# ============================================================

importancias = pd.DataFrame({
    "variavel": features,
    "importancia": (
        modelo_rf
        .feature_importances_
    ),
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
# 17. PREVISÕES
# ============================================================

previsoes = teste[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "saldo_empregos",
        "saldo_empregos_proximo_ano",
        target,
    ]
].copy()


previsoes = previsoes.rename(
    columns={
        "saldo_empregos": "saldo_2022",
        "saldo_empregos_proximo_ano": "saldo_real_2023",
        target: "variacao_real",
    }
)


previsoes[
    "variacao_baseline"
] = baseline_delta

previsoes[
    "variacao_linear"
] = pred_linear

previsoes[
    "variacao_ridge"
] = pred_ridge

previsoes[
    "variacao_random_forest"
] = pred_rf


# ============================================================
# 18. RECONSTRUÇÃO DO SALDO FUTURO
# ============================================================

previsoes[
    "saldo_previsto_baseline"
] = (
    previsoes["saldo_2022"]
    + previsoes["variacao_baseline"]
)

previsoes[
    "saldo_previsto_linear"
] = (
    previsoes["saldo_2022"]
    + previsoes["variacao_linear"]
)

previsoes[
    "saldo_previsto_ridge"
] = (
    previsoes["saldo_2022"]
    + previsoes["variacao_ridge"]
)

previsoes[
    "saldo_previsto_random_forest"
] = (
    previsoes["saldo_2022"]
    + previsoes["variacao_random_forest"]
)


# ============================================================
# 19. ERRO RANDOM FOREST
# ============================================================

previsoes[
    "erro_rf"
] = (
    previsoes["saldo_real_2023"]
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
            "saldo_2022",
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
# 20. SALVAMENTO
# ============================================================

ARQUIVO_RESULTADOS = (
    OUTPUT_DIR
    / "comparacao_modelos_macro_02.csv"
)

ARQUIVO_PREVISOES = (
    OUTPUT_DIR
    / "previsoes_2023_macro_02.csv"
)

ARQUIVO_IMPORTANCIAS = (
    OUTPUT_DIR
    / "importancia_variaveis_rf_macro_02.csv"
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


print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)

print(ARQUIVO_RESULTADOS)
print(ARQUIVO_PREVISOES)
print(ARQUIVO_IMPORTANCIAS)

print(
    "\nModelo Macro 02 concluído com sucesso."
)