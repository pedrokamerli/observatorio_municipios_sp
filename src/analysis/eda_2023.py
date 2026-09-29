from pathlib import Path

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


# ============================================================
# 2. LEITURA
# ============================================================

df = pd.read_csv(ARQUIVO)


print("\n" + "=" * 60)
print("BASE ANALÍTICA")
print("=" * 60)

print("\nDimensão:")
print(df.shape)

print("\nColunas:")
print(df.columns.tolist())

print("\nPrimeiras linhas:")
print(df.head())


# ============================================================
# 3. ESTATÍSTICAS DESCRITIVAS
# ============================================================

variaveis = [
    "populacao_2022",
    "pib",
    "pib_per_capita",
    "admissoes",
    "desligamentos",
    "saldo_empregos",
    "admissoes_por_1000_hab",
    "desligamentos_por_1000_hab",
    "saldo_empregos_por_1000_hab",
]

print("\n" + "=" * 60)
print("ESTATÍSTICAS DESCRITIVAS")
print("=" * 60)

print(
    df[variaveis]
    .describe()
    .T
)


# ============================================================
# 4. MEDIANA DAS PRINCIPAIS VARIÁVEIS
# ============================================================

print("\n" + "=" * 60)
print("MEDIANAS")
print("=" * 60)

print(
    df[variaveis]
    .median()
)


# ============================================================
# 5. MUNICÍPIOS COM MAIOR PIB
# ============================================================

print("\n" + "=" * 60)
print("MAIORES PIBs")
print("=" * 60)

print(
    df[
        [
            "municipio",
            "populacao_2022",
            "pib",
            "pib_per_capita",
        ]
    ]
    .sort_values(
        "pib",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 6. MAIORES PIBs PER CAPITA
# ============================================================

print("\n" + "=" * 60)
print("MAIORES PIBs PER CAPITA")
print("=" * 60)

print(
    df[
        [
            "municipio",
            "populacao_2022",
            "pib",
            "pib_per_capita",
        ]
    ]
    .sort_values(
        "pib_per_capita",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 7. MAIORES SALDOS DE EMPREGO ABSOLUTOS
# ============================================================

print("\n" + "=" * 60)
print("MAIORES SALDOS ABSOLUTOS")
print("=" * 60)

print(
    df[
        [
            "municipio",
            "populacao_2022",
            "pib",
            "pib_per_capita",
            "saldo_empregos",
        ]
    ]
    .sort_values(
        "saldo_empregos",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 8. MENORES SALDOS DE EMPREGO ABSOLUTOS
# ============================================================

print("\n" + "=" * 60)
print("MENORES SALDOS ABSOLUTOS")
print("=" * 60)

print(
    df[
        [
            "municipio",
            "populacao_2022",
            "pib",
            "pib_per_capita",
            "saldo_empregos",
        ]
    ]
    .sort_values(
        "saldo_empregos",
        ascending=True
    )
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 9. MAIORES SALDOS POR 1.000 HABITANTES
# ============================================================

print("\n" + "=" * 60)
print("MAIORES SALDOS POR 1.000 HABITANTES")
print("=" * 60)

print(
    df[
        [
            "municipio",
            "populacao_2022",
            "pib_per_capita",
            "saldo_empregos",
            "saldo_empregos_por_1000_hab",
        ]
    ]
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=False
    )
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 10. MENORES SALDOS POR 1.000 HABITANTES
# ============================================================

print("\n" + "=" * 60)
print("MENORES SALDOS POR 1.000 HABITANTES")
print("=" * 60)

print(
    df[
        [
            "municipio",
            "populacao_2022",
            "pib_per_capita",
            "saldo_empregos",
            "saldo_empregos_por_1000_hab",
        ]
    ]
    .sort_values(
        "saldo_empregos_por_1000_hab",
        ascending=True
    )
    .head(15)
    .to_string(index=False)
)


# ============================================================
# 11. CORRELAÇÕES
# ============================================================

variaveis_correlacao = [
    "populacao_2022",
    "pib",
    "pib_per_capita",
    "admissoes",
    "desligamentos",
    "saldo_empregos",
    "saldo_empregos_por_1000_hab",
]

correlacoes = (
    df[variaveis_correlacao]
    .corr()
)

print("\n" + "=" * 60)
print("MATRIZ DE CORRELAÇÃO")
print("=" * 60)

print(
    correlacoes.round(3)
)


# ============================================================
# 12. CORRELAÇÃO COM SALDO ABSOLUTO
# ============================================================

print("\n" + "=" * 60)
print("CORRELAÇÕES COM SALDO DE EMPREGOS")
print("=" * 60)

print(
    correlacoes[
        "saldo_empregos"
    ]
    .sort_values(
        ascending=False
    )
)


# ============================================================
# 13. CORRELAÇÃO COM SALDO POR 1.000 HABITANTES
# ============================================================

print("\n" + "=" * 60)
print("CORRELAÇÕES COM SALDO POR 1.000 HABITANTES")
print("=" * 60)

print(
    correlacoes[
        "saldo_empregos_por_1000_hab"
    ]
    .sort_values(
        ascending=False
    )
)


# ============================================================
# 14. SEPARAÇÃO POR PORTE POPULACIONAL
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
# 15. RESUMO POR PORTE
# ============================================================

resumo_porte = (
    df.groupby(
        "faixa_populacional",
        observed=True
    )
    .agg(
        municipios=(
            "codigo_ibge",
            "count"
        ),
        populacao_mediana=(
            "populacao_2022",
            "median"
        ),
        pib_per_capita_mediano=(
            "pib_per_capita",
            "median"
        ),
        saldo_total=(
            "saldo_empregos",
            "sum"
        ),
        saldo_mediano=(
            "saldo_empregos",
            "median"
        ),
        saldo_por_1000_mediano=(
            "saldo_empregos_por_1000_hab",
            "median"
        ),
    )
    .reset_index()
)


print("\n" + "=" * 60)
print("RESUMO POR PORTE POPULACIONAL")
print("=" * 60)

print(
    resumo_porte.to_string(
        index=False
    )
)


# ============================================================
# 16. MUNICÍPIOS COM SALDO POSITIVO, NEGATIVO OU ZERO
# ============================================================

positivos = (
    df["saldo_empregos"] > 0
).sum()

negativos = (
    df["saldo_empregos"] < 0
).sum()

zero = (
    df["saldo_empregos"] == 0
).sum()


print("\n" + "=" * 60)
print("DISTRIBUIÇÃO DO SALDO")
print("=" * 60)

print(
    f"Saldo positivo: {positivos}"
)

print(
    f"Saldo negativo: {negativos}"
)

print(
    f"Saldo zero: {zero}"
)

print(
    f"Total: {len(df)}"
)


# ============================================================
# 17. VALIDAÇÃO
# ============================================================

if (
    positivos
    + negativos
    + zero
    != len(df)
):
    raise ValueError(
        "A classificação dos saldos não cobre toda a base."
    )


print("\nAnálise exploratória concluída com sucesso.")