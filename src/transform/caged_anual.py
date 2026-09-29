from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CAGED_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
    / "2023"
)

MAPA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "mapa_municipios_sp.csv"
)

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. LEITURA DO MAPA DE MUNICÍPIOS
# ============================================================

mapa = pd.read_csv(MAPA_FILE)


# ============================================================
# 3. FUNÇÃO PARA PROCESSAR UM MÊS
# ============================================================

def processar_mes(competencia, mapa):
    pasta = CAGED_DIR / str(competencia)

    arquivo = pasta / f"CAGEDMOV{competencia}.txt"

    print("\n" + "=" * 60)
    print(f"Processando competência {competencia}")
    print("=" * 60)

    print("\nArquivo:")
    print(arquivo)

    # Fail fast:
    # se faltar algum mês, o pipeline para imediatamente
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )

    # Colunas necessárias para nosso objetivo
    colunas = [
        "competênciamov",
        "uf",
        "município",
        "saldomovimentação",
    ]

    # Leitura otimizada
    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="utf-8",
        usecols=colunas
    )

    print("\nDimensão do arquivo original:")
    print(df.shape)

    # ========================================================
    # FILTRO DE SÃO PAULO
    # ========================================================

    sp = df[
        df["uf"] == 35
    ].copy()

    print("\nMovimentações em São Paulo:")
    print(sp.shape)

    # ========================================================
    # CRIAÇÃO DOS INDICADORES
    # ========================================================

    sp["admissao"] = (
        sp["saldomovimentação"] == 1
    ).astype("int8")

    sp["desligamento"] = (
        sp["saldomovimentação"] == -1
    ).astype("int8")

    # ========================================================
    # AGREGAÇÃO POR MUNICÍPIO
    # ========================================================

    mensal = (
        sp.groupby(
            ["competênciamov", "município"],
            as_index=False
        )
        .agg(
            admissoes=("admissao", "sum"),
            desligamentos=("desligamento", "sum"),
            saldo_empregos=("saldomovimentação", "sum"),
        )
    )

    # ========================================================
    # CRIAÇÃO DE ANO E MÊS
    # ========================================================

    mensal["ano"] = (
        mensal["competênciamov"] // 100
    )

    mensal["mes"] = (
        mensal["competênciamov"] % 100
    )

    # ========================================================
    # PADRONIZAÇÃO DO CÓDIGO
    # ========================================================

    mensal = mensal.rename(
        columns={
            "município": "codigo_caged"
        }
    )

    # ========================================================
    # MERGE COM MAPA CAGED -> IBGE
    # ========================================================

    mensal = mensal.merge(
        mapa,
        on="codigo_caged",
        how="left",
        validate="one_to_one",
        indicator=True
    )

    # ========================================================
    # VALIDAÇÃO DO MERGE
    # ========================================================

    print("\nResultado do merge:")
    print(
        mensal["_merge"]
        .value_counts()
    )

    codigos_ausentes = (
        mensal["codigo_ibge"]
        .isna()
        .sum()
    )

    print("\nCódigos IBGE ausentes:")
    print(codigos_ausentes)

    if codigos_ausentes > 0:
        raise ValueError(
            f"Foram encontrados {codigos_ausentes} códigos IBGE ausentes."
        )

    # Remove coluna técnica do merge
    mensal = mensal.drop(
        columns="_merge"
    )

    # ========================================================
    # ORGANIZAÇÃO DAS COLUNAS
    # ========================================================

    mensal = mensal[
        [
            "ano",
            "mes",
            "competênciamov",
            "codigo_ibge",
            "codigo_caged",
            "municipio",
            "admissoes",
            "desligamentos",
            "saldo_empregos",
        ]
    ]

    # ========================================================
    # VALIDAÇÕES DO MÊS
    # ========================================================

    print("\nDimensão final do mês:")
    print(mensal.shape)

    print("\nMunicípios únicos:")
    print(
        mensal["codigo_ibge"]
        .nunique()
    )

    print("\nTotal de admissões:")
    print(
        mensal["admissoes"]
        .sum()
    )

    print("\nTotal de desligamentos:")
    print(
        mensal["desligamentos"]
        .sum()
    )

    print("\nSaldo:")
    print(
        mensal["saldo_empregos"]
        .sum()
    )

    total_movimentacoes_agregadas = (
        mensal["admissoes"].sum()
        + mensal["desligamentos"].sum()
    )

    total_movimentacoes_originais = len(sp)

    print("\nTotal agregado de movimentações:")
    print(total_movimentacoes_agregadas)

    print("\nTotal original de movimentações:")
    print(total_movimentacoes_originais)

    totais_conferem = (
        total_movimentacoes_agregadas
        == total_movimentacoes_originais
    )

    print("\nOs totais conferem?")
    print(totais_conferem)

    if not totais_conferem:
        raise ValueError(
            f"As movimentações não conferem na competência {competencia}."
        )

    return mensal


# ============================================================
# 4. COMPETÊNCIAS DE 2023
# ============================================================

competencias = [
    202301,
    202302,
    202303,
    202304,
    202305,
    202306,
    202307,
    202308,
    202309,
    202310,
    202311,
    202312,
]


# ============================================================
# 5. PROCESSAMENTO DOS 12 MESES
# ============================================================

bases_mensais = []

for competencia in competencias:
    mensal = processar_mes(
        competencia,
        mapa
    )

    bases_mensais.append(mensal)


# ============================================================
# 6. CONCATENAÇÃO DOS MESES
# ============================================================

caged_mensal_2023 = pd.concat(
    bases_mensais,
    ignore_index=True
)


# ============================================================
# 7. VALIDAÇÕES DA BASE MENSAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DA BASE MENSAL CONSOLIDADA")
print("=" * 60)

print("\nPrimeiras linhas:")
print(
    caged_mensal_2023.head()
)

print("\nDimensão:")
print(
    caged_mensal_2023.shape
)

print("\nMeses processados:")
print(
    sorted(
        caged_mensal_2023["mes"]
        .unique()
    )
)

print("\nQuantidade de registros por mês:")
print(
    caged_mensal_2023
    .groupby("mes")
    .size()
)

print("\nMunicípios únicos por mês:")
print(
    caged_mensal_2023
    .groupby("mes")["codigo_ibge"]
    .nunique()
)

print("\nDuplicidades Município + Ano + Mês:")
print(
    caged_mensal_2023
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
            "mes",
        ]
    )
    .sum()
)


# ============================================================
# 8. AGREGAÇÃO ANUAL
# ============================================================

caged_anual_2023 = (
    caged_mensal_2023
    .groupby(
        [
            "ano",
            "codigo_ibge",
            "codigo_caged",
            "municipio",
        ],
        as_index=False
    )
    .agg(
        admissoes=("admissoes", "sum"),
        desligamentos=("desligamentos", "sum"),
        saldo_empregos=("saldo_empregos", "sum"),
    )
)


# ============================================================
# 9. VALIDAÇÕES DA BASE ANUAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DA BASE ANUAL")
print("=" * 60)

print("\nPrimeiras linhas:")
print(
    caged_anual_2023.head()
)

print("\nDimensão anual:")
print(
    caged_anual_2023.shape
)

print("\nMunicípios únicos:")
print(
    caged_anual_2023["codigo_ibge"]
    .nunique()
)

print("\nDuplicidades Município + Ano:")
print(
    caged_anual_2023
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)

total_admissoes = (
    caged_anual_2023["admissoes"]
    .sum()
)

total_desligamentos = (
    caged_anual_2023["desligamentos"]
    .sum()
)

saldo_registrado = (
    caged_anual_2023["saldo_empregos"]
    .sum()
)

saldo_calculado = (
    total_admissoes
    - total_desligamentos
)

print("\nAdmissões em 2023:")
print(total_admissoes)

print("\nDesligamentos em 2023:")
print(total_desligamentos)

print("\nSaldo registrado:")
print(saldo_registrado)

print("\nSaldo calculado:")
print(saldo_calculado)

saldos_conferem = (
    saldo_calculado
    == saldo_registrado
)

print("\nOs saldos conferem?")
print(saldos_conferem)

if not saldos_conferem:
    raise ValueError(
        "O saldo anual calculado não confere com o saldo registrado."
    )


# ============================================================
# 10. SALVAMENTO DAS BASES
# ============================================================

arquivo_mensal = (
    PROCESSED_DIR
    / "caged_sp_mensal_2023.csv"
)

arquivo_anual = (
    PROCESSED_DIR
    / "caged_sp_2023.csv"
)

caged_mensal_2023.to_csv(
    arquivo_mensal,
    index=False,
    encoding="utf-8-sig"
)

caged_anual_2023.to_csv(
    arquivo_anual,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 11. CONFIRMAÇÃO DO SALVAMENTO
# ============================================================

print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)

print("\nBase mensal:")
print(arquivo_mensal)

print("\nArquivo mensal existe?")
print(
    arquivo_mensal.exists()
)

print("\nBase anual:")
print(arquivo_anual)

print("\nArquivo anual existe?")
print(
    arquivo_anual.exists()
)

print("\nProcessamento concluído com sucesso.")