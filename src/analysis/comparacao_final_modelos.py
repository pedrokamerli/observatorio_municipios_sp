from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELOS_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "modelos"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "comparacao_final_modelos"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


MODELO01_FILE = (
    MODELOS_DIR
    / "comparacao_modelos_macro_01.csv"
)

MODELO02_FILE = (
    MODELOS_DIR
    / "comparacao_modelos_macro_02.csv"
)

MODELO03_FILE = (
    MODELOS_DIR
    / "comparacao_modelos_macro_03.csv"
)

MODELO04_FILE = (
    MODELOS_DIR
    / "comparacao_modelos_macro_04_setorial.csv"
)


# ============================================================
# 2. VALIDAÇÃO DOS ARQUIVOS
# ============================================================

arquivos = {
    "Modelo 01": MODELO01_FILE,
    "Modelo 02": MODELO02_FILE,
    "Modelo 03": MODELO03_FILE,
    "Modelo 04": MODELO04_FILE,
}


print("\n" + "=" * 70)
print("VALIDAÇÃO DOS ARQUIVOS")
print("=" * 70)


for nome, arquivo in arquivos.items():

    print(
        f"{nome}: {arquivo.exists()}"
    )

    if not arquivo.exists():

        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )


# ============================================================
# 3. LEITURA
# ============================================================

modelo01 = pd.read_csv(
    MODELO01_FILE
)

modelo02 = pd.read_csv(
    MODELO02_FILE
)

modelo03 = pd.read_csv(
    MODELO03_FILE
)

modelo04 = pd.read_csv(
    MODELO04_FILE
)


print("\n" + "=" * 70)
print("BASES CARREGADAS")
print("=" * 70)

print("\nModelo 01:")
print(
    modelo01.shape
)

print("\nModelo 02:")
print(
    modelo02.shape
)

print("\nModelo 03:")
print(
    modelo03.shape
)

print("\nModelo 04:")
print(
    modelo04.shape
)


# ============================================================
# 4. PADRONIZAÇÃO DAS MÉTRICAS
# ============================================================

# ------------------------------------------------------------
# MODELO 01
# ------------------------------------------------------------
#
# Neste experimento, a métrica já representa diretamente
# o saldo futuro.

m1 = modelo01.copy()

m1 = m1.rename(
    columns={
        "mae": "mae_comparavel",
        "rmse": "rmse_comparavel",
        "r2": "r2_comparavel",
    }
)


# ------------------------------------------------------------
# MODELO 02
# ------------------------------------------------------------
#
# Utilizamos as métricas do saldo futuro reconstruído.

m2 = modelo02.copy()

m2 = m2.rename(
    columns={
        "mae_saldo_futuro":
            "mae_comparavel",

        "rmse_saldo_futuro":
            "rmse_comparavel",

        "r2_saldo_futuro":
            "r2_comparavel",
    }
)


# ------------------------------------------------------------
# MODELO 03
# ------------------------------------------------------------
#
# Utilizamos as métricas do saldo absoluto reconstruído.

m3 = modelo03.copy()

m3 = m3.rename(
    columns={
        "mae_saldo_absoluto":
            "mae_comparavel",

        "rmse_saldo_absoluto":
            "rmse_comparavel",

        "r2_saldo_absoluto":
            "r2_comparavel",
    }
)


# ------------------------------------------------------------
# MODELO 04
# ------------------------------------------------------------

m4 = modelo04.copy()

m4 = m4.rename(
    columns={
        "mae_saldo_absoluto":
            "mae_comparavel",

        "rmse_saldo_absoluto":
            "rmse_comparavel",

        "r2_saldo_absoluto":
            "r2_comparavel",
    }
)


# ============================================================
# 5. MELHOR CONFIGURAÇÃO DE CADA EXPERIMENTO
# ============================================================

# Critério principal:
# menor MAE comparável.

melhor_m1 = (
    m1
    .sort_values(
        "mae_comparavel"
    )
    .iloc[0]
)


melhor_m2 = (
    m2
    .sort_values(
        "mae_comparavel"
    )
    .iloc[0]
)


melhor_m3 = (
    m3
    .sort_values(
        "mae_comparavel"
    )
    .iloc[0]
)


melhor_m4 = (
    m4
    .sort_values(
        "mae_comparavel"
    )
    .iloc[0]
)


# ============================================================
# 6. TABELA CONSOLIDADA
# ============================================================

comparacao = pd.DataFrame(
    [
        {
            "experimento":
                "Modelo 01",

            "algoritmo":
                melhor_m1["modelo"],

            "mae":
                melhor_m1[
                    "mae_comparavel"
                ],

            "rmse":
                melhor_m1[
                    "rmse_comparavel"
                ],

            "r2":
                melhor_m1[
                    "r2_comparavel"
                ],

            "target":
                "Saldo absoluto do próximo ano",

            "caracteristica":
                "Modelo inicial",
        },

        {
            "experimento":
                "Modelo 02",

            "algoritmo":
                melhor_m2["modelo"],

            "mae":
                melhor_m2[
                    "mae_comparavel"
                ],

            "rmse":
                melhor_m2[
                    "rmse_comparavel"
                ],

            "r2":
                melhor_m2[
                    "r2_comparavel"
                ],

            "target":
                "Variação do saldo",

            "caracteristica":
                "Feature engineering temporal",
        },

        {
            "experimento":
                "Modelo 03",

            "algoritmo":
                melhor_m3["modelo"],

            "mae":
                melhor_m3[
                    "mae_comparavel"
                ],

            "rmse":
                melhor_m3[
                    "rmse_comparavel"
                ],

            "r2":
                melhor_m3[
                    "r2_comparavel"
                ],

            "target":
                "Variação do saldo por 1.000 habitantes",

            "caracteristica":
                "Normalização populacional",
        },

        {
            "experimento":
                "Modelo 04",

            "algoritmo":
                melhor_m4["modelo"],

            "mae":
                melhor_m4[
                    "mae_comparavel"
                ],

            "rmse":
                melhor_m4[
                    "rmse_comparavel"
                ],

            "r2":
                melhor_m4[
                    "r2_comparavel"
                ],

            "target":
                "Variação do saldo por 1.000 habitantes",

            "caracteristica":
                "Estrutura econômica defasada",
        },
    ]
)


# ============================================================
# 7. ORDENAÇÃO
# ============================================================

comparacao = comparacao.sort_values(
    "mae"
).reset_index(
    drop=True
)


print("\n" + "=" * 70)
print("COMPARAÇÃO FINAL DOS EXPERIMENTOS")
print("=" * 70)

print(
    comparacao
    .round(
        {
            "mae": 2,
            "rmse": 2,
            "r2": 4,
        }
    )
    .to_string(
        index=False
    )
)


# ============================================================
# 8. MELHOR RESULTADO GLOBAL
# ============================================================

melhor = comparacao.iloc[0]


print("\n" + "=" * 70)
print("MENOR MAE ENTRE OS EXPERIMENTOS")
print("=" * 70)

print(
    f"Experimento: "
    f"{melhor['experimento']}"
)

print(
    f"Algoritmo: "
    f"{melhor['algoritmo']}"
)

print(
    f"MAE: "
    f"{melhor['mae']:,.2f}"
)

print(
    f"RMSE: "
    f"{melhor['rmse']:,.2f}"
)

print(
    f"R²: "
    f"{melhor['r2']:.4f}"
)


# ============================================================
# 9. COMPARAÇÃO COM BASELINE ORIGINAL
# ============================================================

baseline_original = (
    modelo01[
        modelo01["modelo"]
        .str.contains(
            "Baseline",
            case=False,
            na=False
        )
    ]
    .iloc[0]
)


mae_baseline = (
    baseline_original[
        "mae"
    ]
)


mae_melhor = (
    melhor[
        "mae"
    ]
)


reducao_mae = (
    (
        mae_baseline
        - mae_melhor
    )
    / mae_baseline
    * 100
)


print("\n" + "=" * 70)
print("EVOLUÇÃO EM RELAÇÃO AO BASELINE ORIGINAL")
print("=" * 70)

print(
    f"MAE baseline original: "
    f"{mae_baseline:,.2f}"
)

print(
    f"MAE do melhor experimento: "
    f"{mae_melhor:,.2f}"
)

print(
    f"Redução do MAE: "
    f"{reducao_mae:.2f}%"
)


# ============================================================
# 10. EVOLUÇÃO SEQUENCIAL
# ============================================================

ordem_experimentos = [
    "Modelo 01",
    "Modelo 02",
    "Modelo 03",
    "Modelo 04",
]


evolucao = (
    comparacao
    .set_index(
        "experimento"
    )
    .loc[
        ordem_experimentos
    ]
    .reset_index()
)


evolucao[
    "variacao_mae_vs_anterior_pct"
] = (
    evolucao[
        "mae"
    ]
    .pct_change(
        fill_method=None
    )
    * 100
)


print("\n" + "=" * 70)
print("EVOLUÇÃO SEQUENCIAL DO MAE")
print("=" * 70)

print(
    evolucao[
        [
            "experimento",
            "algoritmo",
            "mae",
            "variacao_mae_vs_anterior_pct",
        ]
    ]
    .round(2)
    .to_string(
        index=False
    )
)


# ============================================================
# 11. GRÁFICO - MAE
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.bar(
    evolucao[
        "experimento"
    ],
    evolucao[
        "mae"
    ]
)

plt.xlabel(
    "Experimento"
)

plt.ylabel(
    "MAE"
)

plt.title(
    "Evolução do erro absoluto médio"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "01_comparacao_mae.png",
    dpi=300
)

plt.close()


# ============================================================
# 12. GRÁFICO - RMSE
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.bar(
    evolucao[
        "experimento"
    ],
    evolucao[
        "rmse"
    ]
)

plt.xlabel(
    "Experimento"
)

plt.ylabel(
    "RMSE"
)

plt.title(
    "Comparação do RMSE entre experimentos"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "02_comparacao_rmse.png",
    dpi=300
)

plt.close()


# ============================================================
# 13. GRÁFICO - R²
# ============================================================

plt.figure(
    figsize=(9, 6)
)

plt.bar(
    evolucao[
        "experimento"
    ],
    evolucao[
        "r2"
    ]
)

plt.xlabel(
    "Experimento"
)

plt.ylabel(
    "R²"
)

plt.title(
    "Comparação do R² entre experimentos"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "03_comparacao_r2.png",
    dpi=300
)

plt.close()


# ============================================================
# 14. TABELA COMPLETA DE TODOS OS MODELOS
# ============================================================

todos_modelos = []


for _, linha in m1.iterrows():

    todos_modelos.append(
        {
            "experimento":
                "Modelo 01",

            "modelo":
                linha["modelo"],

            "mae":
                linha["mae_comparavel"],

            "rmse":
                linha["rmse_comparavel"],

            "r2":
                linha["r2_comparavel"],
        }
    )


for _, linha in m2.iterrows():

    todos_modelos.append(
        {
            "experimento":
                "Modelo 02",

            "modelo":
                linha["modelo"],

            "mae":
                linha["mae_comparavel"],

            "rmse":
                linha["rmse_comparavel"],

            "r2":
                linha["r2_comparavel"],
        }
    )


for _, linha in m3.iterrows():

    todos_modelos.append(
        {
            "experimento":
                "Modelo 03",

            "modelo":
                linha["modelo"],

            "mae":
                linha["mae_comparavel"],

            "rmse":
                linha["rmse_comparavel"],

            "r2":
                linha["r2_comparavel"],
        }
    )


for _, linha in m4.iterrows():

    todos_modelos.append(
        {
            "experimento":
                "Modelo 04",

            "modelo":
                linha["modelo"],

            "mae":
                linha["mae_comparavel"],

            "rmse":
                linha["rmse_comparavel"],

            "r2":
                linha["r2_comparavel"],
        }
    )


todos_modelos = pd.DataFrame(
    todos_modelos
)


todos_modelos = (
    todos_modelos
    .sort_values(
        "mae"
    )
    .reset_index(
        drop=True
    )
)


print("\n" + "=" * 70)
print("TODOS OS MODELOS TESTADOS")
print("=" * 70)

print(
    todos_modelos
    .round(
        {
            "mae": 2,
            "rmse": 2,
            "r2": 4,
        }
    )
    .to_string(
        index=False
    )
)


# ============================================================
# 15. RESUMO METODOLÓGICO
# ============================================================

resumo_metodologico = pd.DataFrame(
    [
        {
            "experimento":
                "Modelo 01",

            "mudanca":
                "Previsão direta do saldo",

            "resultado":
                "Baseline superou os modelos supervisionados",
        },

        {
            "experimento":
                "Modelo 02",

            "mudanca":
                "Feature engineering temporal e previsão da variação",

            "resultado":
                "Modelos supervisionados superaram o baseline",
        },

        {
            "experimento":
                "Modelo 03",

            "mudanca":
                "Normalização por população",

            "resultado":
                "Redução dos erros absolutos e extremos",
        },

        {
            "experimento":
                "Modelo 04",

            "mudanca":
                "Inclusão de estrutura econômica defasada",

            "resultado":
                "Features setoriais acrescentaram informação, "
                "mas pioraram a previsão",
        },
    ]
)


print("\n" + "=" * 70)
print("RESUMO DA EVOLUÇÃO METODOLÓGICA")
print("=" * 70)

print(
    resumo_metodologico
    .to_string(
        index=False
    )
)


# ============================================================
# 16. SALVAMENTO
# ============================================================

comparacao.to_csv(
    OUTPUT_DIR
    / "comparacao_final_experimentos.csv",
    index=False,
    encoding="utf-8-sig"
)


todos_modelos.to_csv(
    OUTPUT_DIR
    / "todos_modelos_testados.csv",
    index=False,
    encoding="utf-8-sig"
)


evolucao.to_csv(
    OUTPUT_DIR
    / "evolucao_modelagem.csv",
    index=False,
    encoding="utf-8-sig"
)


resumo_metodologico.to_csv(
    OUTPUT_DIR
    / "resumo_metodologico.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 17. RELATÓRIO TXT
# ============================================================

RELATORIO_FILE = (
    OUTPUT_DIR
    / "resumo_final_modelagem.txt"
)


with open(
    RELATORIO_FILE,
    "w",
    encoding="utf-8"
) as arquivo:

    arquivo.write(
        "OBSERVATÓRIO DOS MUNICÍPIOS PAULISTAS\n"
    )

    arquivo.write(
        "COMPARAÇÃO FINAL DA MODELAGEM\n\n"
    )

    arquivo.write(
        "Melhor resultado pelo critério de MAE:\n"
    )

    arquivo.write(
        f"Experimento: {melhor['experimento']}\n"
    )

    arquivo.write(
        f"Algoritmo: {melhor['algoritmo']}\n"
    )

    arquivo.write(
        f"MAE: {melhor['mae']:.2f}\n"
    )

    arquivo.write(
        f"RMSE: {melhor['rmse']:.2f}\n"
    )

    arquivo.write(
        f"R²: {melhor['r2']:.4f}\n\n"
    )

    arquivo.write(
        f"Redução do MAE em relação ao baseline "
        f"original: {reducao_mae:.2f}%\n\n"
    )

    arquivo.write(
        "Evolução dos experimentos:\n\n"
    )

    for _, linha in resumo_metodologico.iterrows():

        arquivo.write(
            f"{linha['experimento']}\n"
        )

        arquivo.write(
            f"{linha['mudanca']}\n"
        )

        arquivo.write(
            f"{linha['resultado']}\n\n"
        )


# ============================================================
# 18. FINAL
# ============================================================

print("\n" + "=" * 70)
print("ARQUIVOS GERADOS")
print("=" * 70)

print(
    OUTPUT_DIR
)

print("\nArquivos:")

for arquivo in sorted(
    OUTPUT_DIR.iterdir()
):

    print(
        arquivo.name
    )


print(
    "\nComparação final concluída com sucesso."
)