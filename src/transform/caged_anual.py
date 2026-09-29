from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

ANO = 2023
UF_SP = 35


# ============================================================
# 2. CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CAGED_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
    / str(ANO)
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
# 3. VALIDAÇÃO DOS ARQUIVOS NECESSÁRIOS
# ============================================================

if not MAPA_FILE.exists():
    raise FileNotFoundError(
        f"Mapa de municípios não encontrado: {MAPA_FILE}"
    )


# ============================================================
# 4. LEITURA DO MAPA CAGED -> IBGE
# ============================================================

mapa = pd.read_csv(MAPA_FILE)

print("\nMapa de municípios carregado.")

print("\nDimensão do mapa:")
print(mapa.shape)

print("\nMunicípios no mapa:")
print(mapa["codigo_ibge"].nunique())


# ============================================================
# 5. FUNÇÃO PARA PROCESSAR UM MÊS
# ============================================================

def processar_mes(competencia, mapa_municipios):

    pasta = (
        CAGED_DIR
        / str(competencia)
    )

    arquivo = (
        pasta
        / f"CAGEDMOV{competencia}.txt"
    )

    print("\n" + "=" * 60)
    print(f"Processando competência {competencia}")
    print("=" * 60)

    print("\nArquivo:")
    print(arquivo)

    # --------------------------------------------------------
    # FAIL FAST
    # --------------------------------------------------------

    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )

    # --------------------------------------------------------
    # COLUNAS NECESSÁRIAS
    # --------------------------------------------------------

    colunas = [
        "competênciamov",
        "uf",
        "município",
        "saldomovimentação",
    ]

    # --------------------------------------------------------
    # LEITURA OTIMIZADA
    # --------------------------------------------------------

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="utf-8",
        usecols=colunas
    )

    print("\nDimensão do arquivo original:")
    print(df.shape)

    # --------------------------------------------------------
    # VALIDAÇÃO DA COMPETÊNCIA
    # --------------------------------------------------------

    competencias_encontradas = (
        df["competênciamov"]
        .unique()
    )

    if len(competencias_encontradas) != 1:
        raise ValueError(
            f"Mais de uma competência encontrada "
            f"no arquivo {arquivo.name}: "
            f"{competencias_encontradas}"
        )

    if competencias_encontradas[0] != competencia:
        raise ValueError(
            f"A competência do arquivo não corresponde "
            f"à esperada. "
            f"Esperada: {competencia}. "
            f"Encontrada: {competencias_encontradas[0]}"
        )

    # --------------------------------------------------------
    # FILTRO DE SÃO PAULO
    # --------------------------------------------------------

    sp = df[
        df["uf"] == UF_SP
    ].copy()

    print("\nMovimentações em São Paulo:")
    print(sp.shape)

    # --------------------------------------------------------
    # CRIAÇÃO DOS INDICADORES
    # --------------------------------------------------------

    sp["admissao"] = (
        sp["saldomovimentação"] == 1
    ).astype("int8")

    sp["desligamento"] = (
        sp["saldomovimentação"] == -1
    ).astype("int8")

    # --------------------------------------------------------
    # AGREGAÇÃO MUNICIPAL
    # --------------------------------------------------------

    mensal = (
        sp.groupby(
            [
                "competênciamov",
                "município",
            ],
            as_index=False
        )
        .agg(
            admissoes=(
                "admissao",
                "sum"
            ),
            desligamentos=(
                "desligamento",
                "sum"
            ),
            saldo_empregos=(
                "saldomovimentação",
                "sum"
            ),
        )
    )

    # --------------------------------------------------------
    # CRIAÇÃO DE ANO E MÊS
    # --------------------------------------------------------

    mensal["ano"] = (
        mensal["competênciamov"]
        // 100
    )

    mensal["mes"] = (
        mensal["competênciamov"]
        % 100
    )

    # --------------------------------------------------------
    # PADRONIZAÇÃO DO CÓDIGO
    # --------------------------------------------------------

    mensal = mensal.rename(
        columns={
            "município": "codigo_caged"
        }
    )

    # --------------------------------------------------------
    # MERGE CAGED -> IBGE
    # --------------------------------------------------------

    mensal = mensal.merge(
        mapa_municipios,
        on="codigo_caged",
        how="left",
        validate="one_to_one",
        indicator=True
    )

    # --------------------------------------------------------
    # VALIDAÇÃO DO MERGE
    # --------------------------------------------------------

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

        problemas = mensal[
            mensal["codigo_ibge"]
            .isna()
        ]

        print("\nCódigos sem correspondência:")
        print(problemas)

        raise ValueError(
            f"Foram encontrados "
            f"{codigos_ausentes} "
            f"códigos sem correspondência no IBGE."
        )

    mensal = mensal.drop(
        columns="_merge"
    )

    # --------------------------------------------------------
    # ORGANIZAÇÃO DAS COLUNAS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # VALIDAÇÕES DO MÊS
    # --------------------------------------------------------

    print("\nDimensão final do mês:")
    print(mensal.shape)

    print("\nMunicípios únicos:")
    print(
        mensal["codigo_ibge"]
        .nunique()
    )

    total_admissoes = (
        mensal["admissoes"]
        .sum()
    )

    total_desligamentos = (
        mensal["desligamentos"]
        .sum()
    )

    saldo = (
        mensal["saldo_empregos"]
        .sum()
    )

    print("\nTotal de admissões:")
    print(total_admissoes)

    print("\nTotal de desligamentos:")
    print(total_desligamentos)

    print("\nSaldo:")
    print(saldo)

    # --------------------------------------------------------
    # VALIDAÇÃO DAS MOVIMENTAÇÕES
    # --------------------------------------------------------

    total_movimentacoes_agregadas = (
        total_admissoes
        + total_desligamentos
    )

    total_movimentacoes_originais = (
        len(sp)
    )

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
            f"As movimentações não conferem "
            f"na competência {competencia}."
        )

    # --------------------------------------------------------
    # VALIDAÇÃO DO SALDO
    # --------------------------------------------------------

    saldo_calculado = (
        total_admissoes
        - total_desligamentos
    )

    if saldo_calculado != saldo:
        raise ValueError(
            f"O saldo não confere "
            f"na competência {competencia}."
        )

    return mensal


# ============================================================
# 6. CRIAÇÃO DAS 12 COMPETÊNCIAS
# ============================================================

competencias = [
    ANO * 100 + mes
    for mes in range(1, 13)
]

print("\nCompetências que serão processadas:")
print(competencias)


# ============================================================
# 7. PROCESSAMENTO DOS 12 MESES
# ============================================================

bases_mensais = []

for competencia in competencias:

    mensal = processar_mes(
        competencia,
        mapa
    )

    bases_mensais.append(
        mensal
    )


# ============================================================
# 8. CONCATENAÇÃO DOS 12 MESES
# ============================================================

caged_mensal_original = pd.concat(
    bases_mensais,
    ignore_index=True
)


# ============================================================
# 9. VALIDAÇÃO DA BASE MENSAL ORIGINAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DA BASE MENSAL ORIGINAL")
print("=" * 60)

print("\nDimensão:")
print(
    caged_mensal_original.shape
)

print("\nMeses processados:")
print(
    sorted(
        caged_mensal_original[
            "mes"
        ].unique()
    )
)

print("\nQuantidade de registros por mês:")
print(
    caged_mensal_original
    .groupby("mes")
    .size()
)

print("\nMunicípios únicos por mês:")
print(
    caged_mensal_original
    .groupby("mes")[
        "codigo_ibge"
    ]
    .nunique()
)

print("\nDuplicidades Município + Ano + Mês:")
print(
    caged_mensal_original
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
# 10. IDENTIFICAÇÃO DOS MUNICÍPIOS AUSENTES
# ============================================================

print("\n" + "=" * 60)
print("MUNICÍPIOS AUSENTES POR MÊS")
print("=" * 60)

for mes in range(1, 13):

    codigos_presentes = set(
        caged_mensal_original.loc[
            caged_mensal_original["mes"] == mes,
            "codigo_ibge"
        ]
    )

    faltantes = mapa[
        ~mapa["codigo_ibge"]
        .isin(codigos_presentes)
    ]

    if len(faltantes) > 0:

        print(f"\nMês {mes}:")

        print(
            faltantes[
                [
                    "codigo_caged",
                    "codigo_ibge",
                    "municipio",
                ]
            ].to_string(
                index=False
            )
        )


# ============================================================
# 11. CRIAÇÃO DO PAINEL COMPLETO
#     645 MUNICÍPIOS X 12 MESES
# ============================================================

meses = pd.DataFrame({
    "mes": range(1, 13)
})

municipios_base = mapa[
    [
        "codigo_caged",
        "codigo_ibge",
        "municipio",
    ]
].copy()


# Produto cartesiano:
# cada município combinado com cada mês

painel_completo = municipios_base.merge(
    meses,
    how="cross"
)

painel_completo["ano"] = ANO

painel_completo["competênciamov"] = (
    painel_completo["ano"] * 100
    + painel_completo["mes"]
)


print("\n" + "=" * 60)
print("PAINEL MUNICÍPIO X MÊS")
print("=" * 60)

print("\nDimensão esperada:")
print(
    painel_completo.shape
)


# ============================================================
# 12. MERGE DO PAINEL COM OS DADOS DO CAGED
# ============================================================

colunas_movimentos = [
    "ano",
    "mes",
    "competênciamov",
    "codigo_ibge",
    "admissoes",
    "desligamentos",
    "saldo_empregos",
]

painel_completo = painel_completo.merge(
    caged_mensal_original[
        colunas_movimentos
    ],
    on=[
        "ano",
        "mes",
        "competênciamov",
        "codigo_ibge",
    ],
    how="left",
    validate="one_to_one",
    indicator=True
)


# ============================================================
# 13. VALIDAÇÃO DO PAINEL
# ============================================================

print("\nResultado da reconstrução do painel:")

print(
    painel_completo["_merge"]
    .value_counts()
)


# ============================================================
# 14. IDENTIFICAÇÃO DOS CASOS SEM REGISTRO
# ============================================================

painel_completo[
    "sem_movimentacao_registrada"
] = (
    painel_completo["_merge"]
    == "left_only"
)


print("\nCombinações sem movimentação registrada:")

print(
    painel_completo[
        painel_completo[
            "sem_movimentacao_registrada"
        ]
    ][
        [
            "ano",
            "mes",
            "codigo_ibge",
            "municipio",
        ]
    ].to_string(
        index=False
    )
)


# ============================================================
# 15. PREENCHIMENTO DOS CASOS AUSENTES COM ZERO
# ============================================================

colunas_numericas = [
    "admissoes",
    "desligamentos",
    "saldo_empregos",
]

painel_completo[
    colunas_numericas
] = (
    painel_completo[
        colunas_numericas
    ]
    .fillna(0)
    .astype(int)
)


# Remove coluna técnica
painel_completo = painel_completo.drop(
    columns="_merge"
)


# ============================================================
# 16. ORGANIZAÇÃO DA BASE MENSAL FINAL
# ============================================================

caged_mensal_2023 = painel_completo[
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
        "sem_movimentacao_registrada",
    ]
].sort_values(
    [
        "mes",
        "codigo_ibge",
    ]
).reset_index(
    drop=True
)


# ============================================================
# 17. VALIDAÇÃO DO PAINEL MENSAL FINAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DA BASE MENSAL COMPLETA")
print("=" * 60)

print("\nDimensão:")
print(
    caged_mensal_2023.shape
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
    .groupby("mes")[
        "codigo_ibge"
    ]
    .nunique()
)

print("\nDuplicidades Município + Ano + Mês:")

duplicidades_mensais = (
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

print(
    duplicidades_mensais
)


if duplicidades_mensais != 0:
    raise ValueError(
        "Foram encontradas duplicidades "
        "na base mensal."
    )


# ============================================================
# 18. VALIDAÇÃO DA QUANTIDADE ESPERADA
# ============================================================

municipios_esperados = (
    mapa["codigo_ibge"]
    .nunique()
)

meses_esperados = 12

linhas_esperadas = (
    municipios_esperados
    * meses_esperados
)

linhas_encontradas = (
    len(caged_mensal_2023)
)

print("\nLinhas esperadas:")
print(linhas_esperadas)

print("\nLinhas encontradas:")
print(linhas_encontradas)

if linhas_encontradas != linhas_esperadas:
    raise ValueError(
        "O painel mensal não contém "
        "todas as combinações "
        "Município x Mês."
    )


# ============================================================
# 19. AGREGAÇÃO ANUAL
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
        admissoes=(
            "admissoes",
            "sum"
        ),
        desligamentos=(
            "desligamentos",
            "sum"
        ),
        saldo_empregos=(
            "saldo_empregos",
            "sum"
        ),
    )
)


# ============================================================
# 20. VALIDAÇÃO DA BASE ANUAL
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

municipios_anuais = (
    caged_anual_2023[
        "codigo_ibge"
    ]
    .nunique()
)

print(
    municipios_anuais
)

if municipios_anuais != municipios_esperados:
    raise ValueError(
        "A quantidade de municípios "
        "na base anual não confere."
    )


# ============================================================
# 21. DUPLICIDADES ANUAIS
# ============================================================

duplicidades_anuais = (
    caged_anual_2023
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)

print("\nDuplicidades Município + Ano:")
print(
    duplicidades_anuais
)

if duplicidades_anuais != 0:
    raise ValueError(
        "Existem duplicidades "
        "Município + Ano."
    )


# ============================================================
# 22. TOTAIS ANUAIS
# ============================================================

total_admissoes = (
    caged_anual_2023[
        "admissoes"
    ]
    .sum()
)

total_desligamentos = (
    caged_anual_2023[
        "desligamentos"
    ]
    .sum()
)

saldo_registrado = (
    caged_anual_2023[
        "saldo_empregos"
    ]
    .sum()
)

saldo_calculado = (
    total_admissoes
    - total_desligamentos
)


print("\nAdmissões em 2023:")
print(
    total_admissoes
)

print("\nDesligamentos em 2023:")
print(
    total_desligamentos
)

print("\nSaldo registrado:")
print(
    saldo_registrado
)

print("\nSaldo calculado:")
print(
    saldo_calculado
)


# ============================================================
# 23. VALIDAÇÃO MATEMÁTICA DO SALDO
# ============================================================

saldos_conferem = (
    saldo_calculado
    == saldo_registrado
)

print("\nOs saldos conferem?")
print(
    saldos_conferem
)

if not saldos_conferem:
    raise ValueError(
        "O saldo anual calculado "
        "não confere com o saldo registrado."
    )


# ============================================================
# 24. COMPARAÇÃO COM A BASE ORIGINAL
# ============================================================

admissoes_originais = (
    caged_mensal_original[
        "admissoes"
    ]
    .sum()
)

desligamentos_originais = (
    caged_mensal_original[
        "desligamentos"
    ]
    .sum()
)

saldo_original = (
    caged_mensal_original[
        "saldo_empregos"
    ]
    .sum()
)

print("\n" + "=" * 60)
print("VALIDAÇÃO APÓS COMPLETAR O PAINEL")
print("=" * 60)

print("\nAdmissões antes:")
print(
    admissoes_originais
)

print("\nAdmissões depois:")
print(
    total_admissoes
)

print("\nDesligamentos antes:")
print(
    desligamentos_originais
)

print("\nDesligamentos depois:")
print(
    total_desligamentos
)

print("\nSaldo antes:")
print(
    saldo_original
)

print("\nSaldo depois:")
print(
    saldo_registrado
)


if (
    admissoes_originais
    != total_admissoes
):
    raise ValueError(
        "O total de admissões mudou "
        "após completar o painel."
    )

if (
    desligamentos_originais
    != total_desligamentos
):
    raise ValueError(
        "O total de desligamentos mudou "
        "após completar o painel."
    )

if (
    saldo_original
    != saldo_registrado
):
    raise ValueError(
        "O saldo mudou após "
        "completar o painel."
    )


# ============================================================
# 25. SALVAMENTO DA BASE MENSAL
# ============================================================

arquivo_mensal = (
    PROCESSED_DIR
    / f"caged_sp_mensal_{ANO}.csv"
)

caged_mensal_2023.to_csv(
    arquivo_mensal,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 26. SALVAMENTO DA BASE ANUAL
# ============================================================

arquivo_anual = (
    PROCESSED_DIR
    / f"caged_sp_{ANO}.csv"
)

caged_anual_2023.to_csv(
    arquivo_anual,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 27. CONFIRMAÇÃO FINAL
# ============================================================

print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)

print("\nBase mensal:")
print(
    arquivo_mensal
)

print("\nArquivo mensal existe?")
print(
    arquivo_mensal.exists()
)

print("\nBase anual:")
print(
    arquivo_anual
)

print("\nArquivo anual existe?")
print(
    arquivo_anual.exists()
)


print("\n" + "=" * 60)
print("PROCESSAMENTO CONCLUÍDO COM SUCESSO")
print("=" * 60)