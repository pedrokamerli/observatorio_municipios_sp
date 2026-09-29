from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

ANOS = [
    2020,
    2021,
    2022,
    2023,
]

UF_SP = 35


# ============================================================
# 2. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CAGED_BASE_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "caged"
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
# 3. LEITURA DO MAPA DE MUNICÍPIOS
# ============================================================

if not MAPA_FILE.exists():
    raise FileNotFoundError(
        f"Mapa de municípios não encontrado: {MAPA_FILE}"
    )

mapa = pd.read_csv(
    MAPA_FILE
)

print("\n" + "=" * 60)
print("MAPA DE MUNICÍPIOS")
print("=" * 60)

print("\nDimensão:")
print(mapa.shape)

print("\nMunicípios únicos:")
print(
    mapa["codigo_ibge"]
    .nunique()
)

print("\nDuplicidades código CAGED:")
print(
    mapa["codigo_caged"]
    .duplicated()
    .sum()
)

print("\nDuplicidades código IBGE:")
print(
    mapa["codigo_ibge"]
    .duplicated()
    .sum()
)


# ============================================================
# 4. FUNÇÃO PARA PROCESSAR UM MÊS
# ============================================================

def processar_mes(ano, mes):

    competencia = (
        ano * 100
        + mes
    )

    arquivo = (
        CAGED_BASE_DIR
        / str(ano)
        / str(competencia)
        / f"CAGEDMOV{competencia}.txt"
    )

    print("\n" + "-" * 60)
    print(f"Processando {competencia}")
    print("-" * 60)

    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )

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

    print("Brasil:", df.shape)

    # --------------------------------------------------------
    # VALIDAÇÃO DA COMPETÊNCIA
    # --------------------------------------------------------

    competencias_encontradas = (
        df["competênciamov"]
        .unique()
    )

    if len(competencias_encontradas) != 1:

        raise ValueError(
            f"Arquivo {arquivo.name} possui "
            f"mais de uma competência: "
            f"{competencias_encontradas}"
        )

    if (
        competencias_encontradas[0]
        != competencia
    ):

        raise ValueError(
            f"Competência incorreta no arquivo. "
            f"Esperada: {competencia}. "
            f"Encontrada: "
            f"{competencias_encontradas[0]}"
        )

    # --------------------------------------------------------
    # FILTRO SP
    # --------------------------------------------------------

    sp = df[
        df["uf"] == UF_SP
    ].copy()

    print("São Paulo:", sp.shape)

    # --------------------------------------------------------
    # VALIDAÇÃO DO SALDO
    # --------------------------------------------------------

    valores_saldo = set(
        sp[
            "saldomovimentação"
        ].unique()
    )

    valores_esperados = {
        -1,
        1,
    }

    valores_inesperados = (
        valores_saldo
        - valores_esperados
    )

    if valores_inesperados:

        raise ValueError(
            f"Valores inesperados em "
            f"saldomovimentação na competência "
            f"{competencia}: "
            f"{valores_inesperados}"
        )

    # --------------------------------------------------------
    # ADMISSÃO / DESLIGAMENTO
    # --------------------------------------------------------

    sp["admissao"] = (
        sp["saldomovimentação"] == 1
    ).astype("int8")

    sp["desligamento"] = (
        sp["saldomovimentação"] == -1
    ).astype("int8")

    # --------------------------------------------------------
    # AGREGAÇÃO POR MUNICÍPIO
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

    mensal["ano"] = ano
    mensal["mes"] = mes

    mensal = mensal.rename(
        columns={
            "município": "codigo_caged"
        }
    )

    # --------------------------------------------------------
    # MERGE COM MAPA DE MUNICÍPIOS
    # --------------------------------------------------------

    mensal = mensal.merge(
        mapa,
        on="codigo_caged",
        how="left",
        validate="one_to_one",
        indicator=True
    )

    codigos_ausentes = (
        mensal[
            "codigo_ibge"
        ]
        .isna()
        .sum()
    )

    if codigos_ausentes > 0:

        print(
            mensal[
                mensal["codigo_ibge"]
                .isna()
            ]
        )

        raise ValueError(
            f"{codigos_ausentes} códigos "
            f"sem correspondência no IBGE "
            f"em {competencia}."
        )

    mensal = mensal.drop(
        columns="_merge"
    )

    # --------------------------------------------------------
    # ORGANIZAÇÃO
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
    # VALIDAÇÃO MATEMÁTICA
    # --------------------------------------------------------

    admissoes = (
        mensal["admissoes"]
        .sum()
    )

    desligamentos = (
        mensal["desligamentos"]
        .sum()
    )

    saldo = (
        mensal["saldo_empregos"]
        .sum()
    )

    movimentacoes = (
        admissoes
        + desligamentos
    )

    if movimentacoes != len(sp):

        raise ValueError(
            f"Total de movimentações não confere "
            f"em {competencia}."
        )

    if (
        admissoes
        - desligamentos
        != saldo
    ):

        raise ValueError(
            f"Saldo não confere "
            f"em {competencia}."
        )

    print(
        f"Municípios com movimentação: "
        f"{mensal['codigo_ibge'].nunique()}"
    )

    print(
        f"Admissões: {admissoes}"
    )

    print(
        f"Desligamentos: {desligamentos}"
    )

    print(
        f"Saldo: {saldo}"
    )

    return mensal


# ============================================================
# 5. FUNÇÃO PARA PROCESSAR UM ANO COMPLETO
# ============================================================

def processar_ano(ano):

    print("\n" + "#" * 60)
    print(f"PROCESSANDO ANO {ano}")
    print("#" * 60)

    bases_mensais = []

    for mes in range(1, 13):

        mensal = processar_mes(
            ano,
            mes
        )

        bases_mensais.append(
            mensal
        )

    # --------------------------------------------------------
    # CONCATENA OS 12 MESES
    # --------------------------------------------------------

    mensal_original = pd.concat(
        bases_mensais,
        ignore_index=True
    )

    print("\n" + "=" * 60)
    print(f"BASE MENSAL ORIGINAL - {ano}")
    print("=" * 60)

    print("\nDimensão:")
    print(
        mensal_original.shape
    )

    print("\nMunicípios por mês:")

    print(
        mensal_original
        .groupby("mes")[
            "codigo_ibge"
        ]
        .nunique()
    )

    # --------------------------------------------------------
    # CRIA PAINEL COMPLETO
    # --------------------------------------------------------

    meses = pd.DataFrame({
        "mes": range(1, 13)
    })

    municipios = mapa[
        [
            "codigo_caged",
            "codigo_ibge",
            "municipio",
        ]
    ].copy()

    painel = municipios.merge(
        meses,
        how="cross"
    )

    painel["ano"] = ano

    painel["competênciamov"] = (
        painel["ano"] * 100
        + painel["mes"]
    )

    # --------------------------------------------------------
    # JUNTA MOVIMENTAÇÕES
    # --------------------------------------------------------

    colunas_movimentos = [
        "ano",
        "mes",
        "competênciamov",
        "codigo_ibge",
        "admissoes",
        "desligamentos",
        "saldo_empregos",
    ]

    painel = painel.merge(
        mensal_original[
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

    # --------------------------------------------------------
    # IDENTIFICA AUSÊNCIAS
    # --------------------------------------------------------

    painel[
        "sem_movimentacao_registrada"
    ] = (
        painel["_merge"]
        == "left_only"
    )

    ausentes = painel[
        painel[
            "sem_movimentacao_registrada"
        ]
    ]

    print("\nCombinações Município-Mês sem registro:")
    print(
        len(ausentes)
    )

    if len(ausentes) > 0:

        print(
            ausentes[
                [
                    "ano",
                    "mes",
                    "codigo_ibge",
                    "municipio",
                ]
            ]
            .to_string(
                index=False
            )
        )

    # --------------------------------------------------------
    # COMPLETA AUSÊNCIAS COM ZERO
    # --------------------------------------------------------

    colunas_numericas = [
        "admissoes",
        "desligamentos",
        "saldo_empregos",
    ]

    painel[
        colunas_numericas
    ] = (
        painel[
            colunas_numericas
        ]
        .fillna(0)
        .astype("int64")
    )

    painel = painel.drop(
        columns="_merge"
    )

    mensal_completo = painel[
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
            "ano",
            "mes",
            "codigo_ibge",
        ]
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # VALIDAÇÃO DO PAINEL
    # --------------------------------------------------------

    linhas_esperadas = (
        mapa[
            "codigo_ibge"
        ].nunique()
        * 12
    )

    linhas_encontradas = (
        len(
            mensal_completo
        )
    )

    print("\nLinhas esperadas:")
    print(
        linhas_esperadas
    )

    print("\nLinhas encontradas:")
    print(
        linhas_encontradas
    )

    if (
        linhas_encontradas
        != linhas_esperadas
    ):

        raise ValueError(
            f"Painel de {ano} incompleto."
        )

    duplicidades = (
        mensal_completo
        .duplicated(
            subset=[
                "codigo_ibge",
                "ano",
                "mes",
            ]
        )
        .sum()
    )

    if duplicidades != 0:

        raise ValueError(
            f"Duplicidades encontradas "
            f"no painel de {ano}."
        )

    # --------------------------------------------------------
    # AGREGAÇÃO ANUAL
    # --------------------------------------------------------

    anual = (
        mensal_completo
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

    # --------------------------------------------------------
    # VALIDAÇÕES ANUAIS
    # --------------------------------------------------------

    municipios_anuais = (
        anual[
            "codigo_ibge"
        ]
        .nunique()
    )

    if municipios_anuais != 645:

        raise ValueError(
            f"O ano {ano} possui "
            f"{municipios_anuais} municípios."
        )

    if (
        anual
        .duplicated(
            subset=[
                "ano",
                "codigo_ibge",
            ]
        )
        .sum()
        != 0
    ):

        raise ValueError(
            f"Duplicidades anuais "
            f"em {ano}."
        )

    total_admissoes = (
        anual[
            "admissoes"
        ]
        .sum()
    )

    total_desligamentos = (
        anual[
            "desligamentos"
        ]
        .sum()
    )

    saldo = (
        anual[
            "saldo_empregos"
        ]
        .sum()
    )

    if (
        total_admissoes
        - total_desligamentos
        != saldo
    ):

        raise ValueError(
            f"Saldo anual não confere "
            f"em {ano}."
        )

    # Garante que completar o painel
    # não alterou os totais originais

    if (
        mensal_original[
            "admissoes"
        ].sum()
        != total_admissoes
    ):

        raise ValueError(
            f"Admissões foram alteradas "
            f"ao completar o painel de {ano}."
        )

    if (
        mensal_original[
            "desligamentos"
        ].sum()
        != total_desligamentos
    ):

        raise ValueError(
            f"Desligamentos foram alterados "
            f"ao completar o painel de {ano}."
        )

    print("\n" + "=" * 60)
    print(f"RESUMO ANUAL - {ano}")
    print("=" * 60)

    print(
        f"Municípios: "
        f"{municipios_anuais}"
    )

    print(
        f"Admissões: "
        f"{total_admissoes}"
    )

    print(
        f"Desligamentos: "
        f"{total_desligamentos}"
    )

    print(
        f"Saldo: "
        f"{saldo}"
    )

    return (
        mensal_completo,
        anual
    )


# ============================================================
# 6. PROCESSAMENTO DOS ANOS
# ============================================================

bases_mensais = []
bases_anuais = []

for ano in ANOS:

    mensal_ano, anual_ano = (
        processar_ano(
            ano
        )
    )

    bases_mensais.append(
        mensal_ano
    )

    bases_anuais.append(
        anual_ano
    )


# ============================================================
# 7. CONSOLIDAÇÃO MULTIANUAL
# ============================================================

caged_mensal = pd.concat(
    bases_mensais,
    ignore_index=True
)

caged_anual = pd.concat(
    bases_anuais,
    ignore_index=True
)


# ============================================================
# 8. VALIDAÇÃO DA BASE MENSAL MULTIANUAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO MULTIANUAL - MENSAL")
print("=" * 60)

print("\nDimensão:")
print(
    caged_mensal.shape
)

print("\nRegistros por ano:")

print(
    caged_mensal
    .groupby("ano")
    .size()
)

print("\nMunicípios por ano:")

print(
    caged_mensal
    .groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)

duplicidades_mensais = (
    caged_mensal
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
            "mes",
        ]
    )
    .sum()
)

print("\nDuplicidades Município + Ano + Mês:")
print(
    duplicidades_mensais
)

if duplicidades_mensais != 0:

    raise ValueError(
        "Existem duplicidades "
        "na base mensal multianual."
    )


# ============================================================
# 9. VALIDAÇÃO DA BASE ANUAL MULTIANUAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO MULTIANUAL - ANUAL")
print("=" * 60)

print("\nDimensão:")
print(
    caged_anual.shape
)

print("\nMunicípios por ano:")

print(
    caged_anual
    .groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)

print("\nRegistros por ano:")

print(
    caged_anual
    .groupby("ano")
    .size()
)

duplicidades_anuais = (
    caged_anual
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
        "na base anual multianual."
    )


# ============================================================
# 10. VALIDAÇÃO DAS DIMENSÕES ESPERADAS
# ============================================================

municipios = (
    mapa[
        "codigo_ibge"
    ]
    .nunique()
)

linhas_mensais_esperadas = (
    municipios
    * 12
    * len(ANOS)
)

linhas_anuais_esperadas = (
    municipios
    * len(ANOS)
)

print("\nLinhas mensais esperadas:")
print(
    linhas_mensais_esperadas
)

print("\nLinhas mensais encontradas:")
print(
    len(
        caged_mensal
    )
)

print("\nLinhas anuais esperadas:")
print(
    linhas_anuais_esperadas
)

print("\nLinhas anuais encontradas:")
print(
    len(
        caged_anual
    )
)


if (
    len(caged_mensal)
    != linhas_mensais_esperadas
):

    raise ValueError(
        "Quantidade de linhas mensais "
        "não corresponde ao esperado."
    )


if (
    len(caged_anual)
    != linhas_anuais_esperadas
):

    raise ValueError(
        "Quantidade de linhas anuais "
        "não corresponde ao esperado."
    )


# ============================================================
# 11. RESUMO DO MERCADO DE TRABALHO POR ANO
# ============================================================

resumo_anual = (
    caged_anual
    .groupby(
        "ano",
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


print("\n" + "=" * 60)
print("RESUMO DO CAGED POR ANO")
print("=" * 60)

print(
    resumo_anual
    .to_string(
        index=False
    )
)


# ============================================================
# 12. SALVAMENTO
# ============================================================

ARQUIVO_MENSAL = (
    PROCESSED_DIR
    / "caged_sp_mensal_2020_2023.csv"
)

ARQUIVO_ANUAL = (
    PROCESSED_DIR
    / "caged_sp_anual_2020_2023.csv"
)

caged_mensal.to_csv(
    ARQUIVO_MENSAL,
    index=False,
    encoding="utf-8-sig"
)

caged_anual.to_csv(
    ARQUIVO_ANUAL,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 13. FINAL
# ============================================================

print("\n" + "=" * 60)
print("ARQUIVOS GERADOS")
print("=" * 60)

print("\nBase mensal:")
print(
    ARQUIVO_MENSAL
)

print("\nExiste?")
print(
    ARQUIVO_MENSAL.exists()
)

print("\nBase anual:")
print(
    ARQUIVO_ANUAL
)

print("\nExiste?")
print(
    ARQUIVO_ANUAL.exists()
)

print("\nProcessamento multianual concluído com sucesso.")