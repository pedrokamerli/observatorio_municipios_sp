from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import TransformedTargetRegressor
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

df = pd.read_csv(
    ARQUIVO
)


print("\n" + "=" * 60)
print("BASE CARREGADA")
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
# 3. VARIÁVEIS DO PRIMEIRO MODELO
# ============================================================

features = [
    "pib",
    "pib_per_capita",
    "admissoes",
    "desligamentos",
    "saldo_empregos",
]

target = (
    "saldo_empregos_proximo_ano"
)


# ============================================================
# 4. BASE DISPONÍVEL PARA MACHINE LEARNING
# ============================================================

dados_ml = df[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        *features,
        target,
    ]
].copy()


# 2023 não possui target porque não temos
# o saldo de 2024 neste painel.

dados_ml = dados_ml[
    dados_ml[target].notna()
].copy()


print("\n" + "=" * 60)
print("BASE DE MACHINE LEARNING")
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
    dados_ml.isna().sum()
)


# ============================================================
# 5. DIVISÃO TEMPORAL
# ============================================================

treino = dados_ml[
    dados_ml["ano"].isin(
        [
            2020,
            2021,
        ]
    )
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

print("\nAnos do treino:")
print(
    sorted(
        treino["ano"].unique()
    )
)

print("\nTeste:")
print(
    teste.shape
)

print("\nAno do teste:")
print(
    sorted(
        teste["ano"].unique()
    )
)


# ============================================================
# 6. X E Y
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
# 7. FUNÇÃO DE AVALIAÇÃO
# ============================================================

def avaliar_modelo(
    nome,
    y_real,
    y_previsto
):

    mae = mean_absolute_error(
        y_real,
        y_previsto
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_real,
            y_previsto
        )
    )

    r2 = r2_score(
        y_real,
        y_previsto
    )

    print("\n" + "=" * 60)
    print(nome)
    print("=" * 60)

    print(
        f"MAE:  {mae:,.2f}"
    )

    print(
        f"RMSE: {rmse:,.2f}"
    )

    print(
        f"R²:   {r2:.4f}"
    )

    return {
        "modelo": nome,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
    }


# ============================================================
# 8. BASELINE
# ============================================================

# Hipótese mais simples:
# o saldo do próximo ano será igual
# ao saldo do ano atual.

baseline_pred = (
    X_test[
        "saldo_empregos"
    ]
    .to_numpy()
)


resultados = []

resultados.append(
    avaliar_modelo(
        "Baseline - saldo do ano anterior",
        y_test,
        baseline_pred
    )
)


# ============================================================
# 9. REGRESSÃO LINEAR
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
        pred_linear
    )
)


# ============================================================
# 10. RIDGE
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
                alpha=1.0
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
        pred_ridge
    )
)


# ============================================================
# 11. RANDOM FOREST
# ============================================================

modelo_rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_leaf=2,
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
        pred_rf
    )
)


# ============================================================
# 12. COMPARAÇÃO DOS MODELOS
# ============================================================

resultados_df = pd.DataFrame(
    resultados
)

resultados_df = (
    resultados_df
    .sort_values(
        "mae"
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
# 13. IMPORTÂNCIA DAS VARIÁVEIS - RANDOM FOREST
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
# 14. PREVISÕES MUNICIPAIS
# ============================================================

previsoes = teste[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "saldo_empregos",
        target,
    ]
].copy()

previsoes = previsoes.rename(
    columns={
        target: "saldo_real_2023"
    }
)

previsoes[
    "baseline"
] = baseline_pred

previsoes[
    "regressao_linear"
] = pred_linear

previsoes[
    "ridge"
] = pred_ridge

previsoes[
    "random_forest"
] = pred_rf


# ============================================================
# 15. ERRO DO RANDOM FOREST
# ============================================================

previsoes[
    "erro_rf"
] = (
    previsoes[
        "saldo_real_2023"
    ]
    -
    previsoes[
        "random_forest"
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


# ============================================================
# 16. MAIORES ERROS
# ============================================================

print("\n" + "=" * 60)
print("MAIORES ERROS - RANDOM FOREST")
print("=" * 60)

print(
    previsoes[
        [
            "municipio",
            "saldo_real_2023",
            "random_forest",
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
# 17. SALVAMENTO DOS RESULTADOS
# ============================================================

ARQUIVO_RESULTADOS = (
    OUTPUT_DIR
    / "comparacao_modelos_macro_01.csv"
)

ARQUIVO_PREVISOES = (
    OUTPUT_DIR
    / "previsoes_2023_macro_01.csv"
)

ARQUIVO_IMPORTANCIAS = (
    OUTPUT_DIR
    / "importancia_variaveis_rf_macro_01.csv"
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
    "\nPrimeiro experimento de Machine Learning concluído."
)