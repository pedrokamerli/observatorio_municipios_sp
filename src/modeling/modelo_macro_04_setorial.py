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

MODELO03_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "modelos"
    / "comparacao_modelos_macro_03.csv"
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
print(
    df.shape
)

print("\nAnos:")
print(
    sorted(
        df["ano"].unique()
    )
)


# ============================================================
# 3. ORGANIZAÇÃO TEMPORAL
# ============================================================

df = df.sort_values(
    [
        "codigo_ibge",
        "ano",
    ]
).reset_index(
    drop=True
)


# ============================================================
# 4. FEATURES AUXILIARES
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
# 5. PARTICIPAÇÕES SETORIAIS
# ============================================================

# Essas variáveis já existem no painel.
# Em 2020 e 2021 possuem valores.
# Em 2022 e 2023 ficam ausentes na fonte utilizada.

colunas_setoriais = [
    "participacao_agro_pct",
    "participacao_industria_pct",
    "participacao_servicos_pct",
    "participacao_adm_publica_pct",
]


print("\n" + "=" * 60)
print("DISPONIBILIDADE DOS DADOS SETORIAIS")
print("=" * 60)

for coluna in colunas_setoriais:

    print(f"\n{coluna}")

    print(
        df.groupby("ano")[
            coluna
        ]
        .apply(
            lambda x: x.notna().sum()
        )
    )


# ============================================================
# 6. LAG DAS PARTICIPAÇÕES SETORIAIS
# ============================================================

# Nunca vamos usar a composição futura.
#
# Linha 2021 recebe composição de 2020.
# Linha 2022 recebe composição de 2021.

df[
    "participacao_agro_ano_anterior"
] = (
    df.groupby("codigo_ibge")[
        "participacao_agro_pct"
    ]
    .shift(1)
)


df[
    "participacao_industria_ano_anterior"
] = (
    df.groupby("codigo_ibge")[
        "participacao_industria_pct"
    ]
    .shift(1)
)


df[
    "participacao_servicos_ano_anterior"
] = (
    df.groupby("codigo_ibge")[
        "participacao_servicos_pct"
    ]
    .shift(1)
)


df[
    "participacao_adm_publica_ano_anterior"
] = (
    df.groupby("codigo_ibge")[
        "participacao_adm_publica_pct"
    ]
    .shift(1)
)


# ============================================================
# 7. FEATURES BASE DO MODELO 03
# ============================================================

features_macro = [

    # Economia
    "pib_per_capita",
    "crescimento_pib_pct",
    "crescimento_pib_per_capita_pct",

    # Mercado de trabalho normalizado
    "admissoes_por_1000_hab",
    "desligamentos_por_1000_hab",
    "saldo_por_1000_hab",
    "movimentacoes_por_1000_hab",

    # Histórico
    "saldo_por_1000_ano_anterior",
    "admissoes_por_1000_ano_anterior",
    "desligamentos_por_1000_ano_anterior",

    # Relações
    "razao_admissoes_desligamentos",
    "saldo_sobre_movimentacoes",
]


# ============================================================
# 8. FEATURES SETORIAIS DEFASADAS
# ============================================================

features_setoriais = [
    "participacao_agro_ano_anterior",
    "participacao_industria_ano_anterior",
    "participacao_servicos_ano_anterior",
    "participacao_adm_publica_ano_anterior",
]


# ============================================================
# 9. FEATURES FINAIS
# ============================================================

features = (
    features_macro
    + features_setoriais
)


target = (
    "variacao_saldo_por_1000_proximo_ano"
)


# ============================================================
# 10. BASE DE MODELAGEM
# ============================================================

colunas_modelagem = [
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
    colunas_modelagem
].copy()


# ============================================================
# 11. VALIDAÇÃO DE COLUNAS
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
# 12. REMOVE REGISTROS INCOMPLETOS
# ============================================================

dados_ml = dados_ml.dropna(
    subset=[
        *features,
        target,
    ]
).copy()


print("\n" + "=" * 60)
print("BASE DE MACHINE LEARNING - MODELO 04")
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
# 13. DIVISÃO TEMPORAL
# ============================================================

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

print("\nTeste:")
print(
    teste.shape
)


if len(treino) != 645:

    raise ValueError(
        f"Treino deveria possuir 645 municípios. "
        f"Encontrados: {len(treino)}"
    )


if len(teste) != 645:

    raise ValueError(
        f"Teste deveria possuir 645 municípios. "
        f"Encontrados: {len(teste)}"
    )


# ============================================================
# 14. X E Y
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
# 15. FUNÇÃO DE AVALIAÇÃO
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
    # VARIAÇÃO DA TAXA
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
    # TAXA FUTURA
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
    # SALDO ABSOLUTO RECONSTRUÍDO
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
# 16. VETORES AUXILIARES
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
# 17. RESULTADOS
# ============================================================

resultados = []


# ============================================================
# 18. BASELINE
# ============================================================

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
# 19. REGRESSÃO LINEAR
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
# 20. RIDGE
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
# 21. RANDOM FOREST
# ============================================================

# Mantemos os mesmos hiperparâmetros do Modelo 03.
#
# Isso é importante para uma comparação controlada:
# o que muda são as features setoriais.

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
# 22. COMPARAÇÃO DO MODELO 04
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
print("COMPARAÇÃO - MODELO 04 SETORIAL")
print("=" * 60)


print(
    resultados_df
    .to_string(
        index=False
    )
)


# ============================================================
# 23. FEATURE IMPORTANCE
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
# 24. IMPORTÂNCIA APENAS DAS FEATURES SETORIAIS
# ============================================================

importancias_setoriais = (
    importancias[
        importancias[
            "variavel"
        ]
        .isin(
            features_setoriais
        )
    ]
    .copy()
)


print("\n" + "=" * 60)
print("IMPORTÂNCIA DAS FEATURES SETORIAIS")
print("=" * 60)


print(
    importancias_setoriais
    .to_string(
        index=False
    )
)


print("\nImportância setorial total:")

print(
    round(
        importancias_setoriais[
            "importancia"
        ]
        .sum(),
        6
    )
)


# ============================================================
# 25. PREVISÕES
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
# 26. TAXAS PREVISTAS
# ============================================================

for modelo in [
    "baseline",
    "linear",
    "ridge",
    "random_forest",
]:

    previsoes[
        f"taxa_prevista_{modelo}"
    ] = (

        previsoes[
            "saldo_por_1000_hab"
        ]

        + previsoes[
            f"delta_{modelo}"
        ]

    )


# ============================================================
# 27. SALDO REAL
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
# 28. SALDOS PREVISTOS
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
# 29. ERROS DA RANDOM FOREST
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
print("MAIORES ERROS - MODELO 04")
print("=" * 60)


print(

    previsoes[
        [
            "municipio",
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
# 30. COMPARAÇÃO AUTOMÁTICA COM MODELO 03
# ============================================================

if MODELO03_FILE.exists():

    modelo03 = pd.read_csv(
        MODELO03_FILE
    )


    rf03 = modelo03[
        modelo03["modelo"]
        == "Random Forest"
    ].iloc[0]


    rf04 = resultados_df[
        resultados_df["modelo"]
        == "Random Forest"
    ].iloc[0]


    mae03 = (
        rf03[
            "mae_saldo_absoluto"
        ]
    )

    mae04 = (
        rf04[
            "mae_saldo_absoluto"
        ]
    )


    rmse03 = (
        rf03[
            "rmse_saldo_absoluto"
        ]
    )

    rmse04 = (
        rf04[
            "rmse_saldo_absoluto"
        ]
    )


    r203 = (
        rf03[
            "r2_saldo_absoluto"
        ]
    )

    r204 = (
        rf04[
            "r2_saldo_absoluto"
        ]
    )


    melhoria_mae_pct = (
        (
            mae03
            - mae04
        )
        / mae03
        * 100
    )


    melhoria_rmse_pct = (
        (
            rmse03
            - rmse04
        )
        / rmse03
        * 100
    )


    print("\n" + "=" * 60)
    print("MODELO 03 × MODELO 04 - RANDOM FOREST")
    print("=" * 60)


    print("\nModelo 03:")

    print(
        f"MAE:  {mae03:,.2f}"
    )

    print(
        f"RMSE: {rmse03:,.2f}"
    )

    print(
        f"R²:   {r203:.4f}"
    )


    print("\nModelo 04:")

    print(
        f"MAE:  {mae04:,.2f}"
    )

    print(
        f"RMSE: {rmse04:,.2f}"
    )

    print(
        f"R²:   {r204:.4f}"
    )


    print("\nVariação percentual do MAE:")

    print(
        f"{melhoria_mae_pct:.2f}%"
    )


    print("\nVariação percentual do RMSE:")

    print(
        f"{melhoria_rmse_pct:.2f}%"
    )


# ============================================================
# 31. SALVAMENTO
# ============================================================

ARQUIVO_RESULTADOS = (
    OUTPUT_DIR
    / "comparacao_modelos_macro_04_setorial.csv"
)


ARQUIVO_PREVISOES = (
    OUTPUT_DIR
    / "previsoes_2023_macro_04_setorial.csv"
)


ARQUIVO_IMPORTANCIAS = (
    OUTPUT_DIR
    / "importancia_variaveis_rf_macro_04_setorial.csv"
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
# 32. FINAL
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
    "\nModelo Macro 04 Setorial concluído com sucesso."
)