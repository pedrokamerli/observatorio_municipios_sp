from pathlib import Path

import matplotlib.pyplot as plt
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
    / "base_analitica_sp_2023_com_populacao.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "graficos"
    / "2023"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(ARQUIVO)


# ============================================================
# 3. HISTOGRAMA DO SALDO POR 1.000 HABITANTES
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    df["saldo_empregos_por_1000_hab"],
    bins=40
)

plt.axvline(
    df["saldo_empregos_por_1000_hab"].median(),
    linestyle="--",
    label="Mediana"
)

plt.title(
    "Distribuição do saldo de empregos por 1.000 habitantes"
)

plt.xlabel(
    "Saldo de empregos por 1.000 habitantes"
)

plt.ylabel(
    "Número de municípios"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "01_distribuicao_saldo_por_1000.png",
    dpi=300
)

plt.close()


# ============================================================
# 4. PIB PER CAPITA X SALDO POR 1.000
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    df["pib_per_capita"],
    df["saldo_empregos_por_1000_hab"],
    alpha=0.6
)

plt.title(
    "PIB per capita x geração relativa de empregos"
)

plt.xlabel(
    "PIB per capita (R$)"
)

plt.ylabel(
    "Saldo de empregos por 1.000 habitantes"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "02_pib_per_capita_x_saldo_por_1000.png",
    dpi=300
)

plt.close()


# ============================================================
# 5. PIB PER CAPITA EM ESCALA LOG
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    np.log1p(
        df["pib_per_capita"]
    ),
    df["saldo_empregos_por_1000_hab"],
    alpha=0.6
)

plt.title(
    "PIB per capita (log) x geração relativa de empregos"
)

plt.xlabel(
    "log(PIB per capita)"
)

plt.ylabel(
    "Saldo de empregos por 1.000 habitantes"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "03_log_pib_per_capita_x_saldo_por_1000.png",
    dpi=300
)

plt.close()


# ============================================================
# 6. POPULAÇÃO X SALDO ABSOLUTO
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    np.log1p(
        df["populacao_2022"]
    ),
    df["saldo_empregos"],
    alpha=0.6
)

plt.title(
    "População x saldo absoluto de empregos"
)

plt.xlabel(
    "log(População)"
)

plt.ylabel(
    "Saldo de empregos"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "04_populacao_x_saldo_absoluto.png",
    dpi=300
)

plt.close()


# ============================================================
# 7. POPULAÇÃO X SALDO POR 1.000
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.scatter(
    np.log1p(
        df["populacao_2022"]
    ),
    df["saldo_empregos_por_1000_hab"],
    alpha=0.6
)

plt.title(
    "População x saldo de empregos por 1.000 habitantes"
)

plt.xlabel(
    "log(População)"
)

plt.ylabel(
    "Saldo de empregos por 1.000 habitantes"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "05_populacao_x_saldo_por_1000.png",
    dpi=300
)

plt.close()


# ============================================================
# 8. FAIXAS POPULACIONAIS
# ============================================================

faixas = [
    0,
    10_000,
    50_000,
    100_000,
    500_000,
    float("inf"),
]

rotulos = [
    "Até 10 mil",
    "10 a 50 mil",
    "50 a 100 mil",
    "100 a 500 mil",
    "Acima de 500 mil",
]

df["faixa_populacional"] = pd.cut(
    df["populacao_2022"],
    bins=faixas,
    labels=rotulos,
    right=False,
)


# ============================================================
# 9. BOXPLOT POR PORTE POPULACIONAL
# ============================================================

dados_boxplot = []

for faixa in rotulos:

    valores = df.loc[
        df["faixa_populacional"] == faixa,
        "saldo_empregos_por_1000_hab"
    ]

    dados_boxplot.append(
        valores
    )


plt.figure(
    figsize=(11, 6)
)

plt.boxplot(
    dados_boxplot,
    tick_labels=rotulos,
    showfliers=True
)

plt.title(
    "Saldo de empregos por 1.000 habitantes por porte municipal"
)

plt.xlabel(
    "Faixa populacional"
)

plt.ylabel(
    "Saldo de empregos por 1.000 habitantes"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "06_boxplot_saldo_por_porte.png",
    dpi=300
)

plt.close()


# ============================================================
# 10. TOP 15 SALDO POR 1.000
# ============================================================

top_15 = (
    df
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=False
    )
    .head(15)
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=True
    )
)


plt.figure(
    figsize=(10, 8)
)

plt.barh(
    top_15["municipio"],
    top_15["saldo_empregos_por_1000_hab"]
)

plt.title(
    "15 maiores saldos de empregos por 1.000 habitantes"
)

plt.xlabel(
    "Saldo por 1.000 habitantes"
)

plt.ylabel(
    "Município"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "07_top15_saldo_por_1000.png",
    dpi=300
)

plt.close()


# ============================================================
# 11. 15 MENORES SALDOS POR 1.000
# ============================================================

bottom_15 = (
    df
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=True
    )
    .head(15)
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=False
    )
)


plt.figure(
    figsize=(10, 8)
)

plt.barh(
    bottom_15["municipio"],
    bottom_15["saldo_empregos_por_1000_hab"]
)

plt.title(
    "15 menores saldos de empregos por 1.000 habitantes"
)

plt.xlabel(
    "Saldo por 1.000 habitantes"
)

plt.ylabel(
    "Município"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "08_bottom15_saldo_por_1000.png",
    dpi=300
)

plt.close()


# ============================================================
# 12. TOP 15 PIB PER CAPITA
# ============================================================

top_pib_pc = (
    df
    .sort_values(
        "pib_per_capita",
        ascending=False
    )
    .head(15)
    .sort_values(
        "pib_per_capita",
        ascending=True
    )
)


plt.figure(
    figsize=(10, 8)
)

plt.barh(
    top_pib_pc["municipio"],
    top_pib_pc["pib_per_capita"]
)

plt.title(
    "15 maiores PIBs per capita de São Paulo"
)

plt.xlabel(
    "PIB per capita (R$)"
)

plt.ylabel(
    "Município"
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR
    / "09_top15_pib_per_capita.png",
    dpi=300
)

plt.close()


# ============================================================
# 13. FINAL
# ============================================================

print("\nGráficos gerados com sucesso.")

print("\nPasta:")
print(
    OUTPUT_DIR
)

print("\nArquivos:")

for arquivo in sorted(
    OUTPUT_DIR.glob("*.png")
):

    print(
        arquivo.name
    )
    # ============================================================
    # 14. PIB PER CAPITA X SALDO COM MUNICÍPIOS DESTACADOS
    # ============================================================

    plt.figure(
        figsize=(11, 7)
    )

    plt.scatter(
        df["pib_per_capita"],
        df["saldo_empregos_por_1000_hab"],
        alpha=0.5
    )

    plt.axhline(
        0,
        linestyle="--",
        linewidth=1
    )

    # Maiores saldos relativos
    top_positivos = (
        df
        .nlargest(
            5,
            "saldo_empregos_por_1000_hab"
        )
    )

    # Menores saldos relativos
    top_negativos = (
        df
        .nsmallest(
            5,
            "saldo_empregos_por_1000_hab"
        )
    )

    # Maiores PIBs per capita
    top_pib = (
        df
        .nlargest(
            5,
            "pib_per_capita"
        )
    )

    destaques = pd.concat(
        [
            top_positivos,
            top_negativos,
            top_pib,
        ]
    ).drop_duplicates(
        subset="codigo_ibge"
    )

    for _, linha in destaques.iterrows():
        plt.annotate(
            linha["municipio"],
            (
                linha["pib_per_capita"],
                linha["saldo_empregos_por_1000_hab"]
            ),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    plt.title(
        "PIB per capita e geração relativa de empregos — SP, 2023"
    )

    plt.xlabel(
        "PIB per capita (R$)"
    )

    plt.ylabel(
        "Saldo de empregos por 1.000 habitantes"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "10_pib_per_capita_x_saldo_destaques.png",
        dpi=300
    )

    plt.close()
    # ============================================================
    # 15. POPULAÇÃO X SALDO RELATIVO COM DESTAQUES
    # ============================================================

    plt.figure(
        figsize=(11, 7)
    )

    plt.scatter(
        np.log1p(
            df["populacao_2022"]
        ),
        df["saldo_empregos_por_1000_hab"],
        alpha=0.5
    )

    plt.axhline(
        0,
        linestyle="--",
        linewidth=1
    )

    destaques_pop = pd.concat(
        [
            df.nlargest(
                5,
                "saldo_empregos_por_1000_hab"
            ),
            df.nsmallest(
                5,
                "saldo_empregos_por_1000_hab"
            ),
        ]
    ).drop_duplicates(
        subset="codigo_ibge"
    )

    for _, linha in destaques_pop.iterrows():
        plt.annotate(
            linha["municipio"],
            (
                np.log1p(
                    linha["populacao_2022"]
                ),
                linha["saldo_empregos_por_1000_hab"]
            ),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    plt.title(
        "Porte populacional e geração relativa de empregos — SP, 2023"
    )

    plt.xlabel(
        "log(População)"
    )

    plt.ylabel(
        "Saldo de empregos por 1.000 habitantes"
    )

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR
        / "11_populacao_x_saldo_destaques.png",
        dpi=300
    )

    plt.close()