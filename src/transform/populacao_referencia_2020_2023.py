from pathlib import Path
import unicodedata

import pandas as pd
import requests


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

MAPA_FILE = (
    PROCESSED_DIR
    / "mapa_municipios_sp.csv"
)

POP_2022_FILE = (
    PROCESSED_DIR
    / "ibge_populacao_sp_2022.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "populacao_referencia_sp_2020_2023.csv"
)


# ============================================================
# 2. FUNÇÃO AUXILIAR
# ============================================================

def normalizar_texto(texto):
    texto = str(texto)

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    return texto.lower()


# ============================================================
# 3. MAPA DOS MUNICÍPIOS
# ============================================================

mapa = pd.read_csv(
    MAPA_FILE
)

mapa = mapa[
    [
        "codigo_ibge",
        "municipio",
    ]
].copy()


print("\n" + "=" * 60)
print("MAPA DE MUNICÍPIOS")
print("=" * 60)

print("\nDimensão:")
print(
    mapa.shape
)

print("\nMunicípios:")
print(
    mapa["codigo_ibge"]
    .nunique()
)


# ============================================================
# 4. POPULAÇÃO ESTIMADA 2020 E 2021
# ============================================================

URL = (
    "https://apisidra.ibge.gov.br/"
    "values/t/6579/"
    "n6/all/"
    "v/9324/"
    "p/2020,2021"
    "?formato=json"
)


print("\n" + "=" * 60)
print("DOWNLOAD SIDRA - 2020 E 2021")
print("=" * 60)

resposta = requests.get(
    URL,
    timeout=120
)

print("\nHTTP:")
print(
    resposta.status_code
)

resposta.raise_for_status()

dados = resposta.json()


if len(dados) <= 1:

    raise ValueError(
        "A API SIDRA não retornou dados."
    )


# ============================================================
# 5. IDENTIFICAÇÃO DAS COLUNAS
# ============================================================

cabecalho = dados[0]

print("\nCabeçalho retornado pelo SIDRA:")

for codigo, descricao in cabecalho.items():

    print(
        codigo,
        "->",
        descricao
    )


def encontrar_coluna(
    palavra,
    precisa_codigo=False
):

    for codigo, descricao in cabecalho.items():

        descricao_normalizada = (
            normalizar_texto(
                descricao
            )
        )

        if palavra in descricao_normalizada:

            tem_codigo = (
                "codigo"
                in descricao_normalizada
            )

            if (
                precisa_codigo
                and tem_codigo
            ):
                return codigo

            if (
                not precisa_codigo
                and not tem_codigo
            ):
                return codigo

    return None


col_codigo_municipio = encontrar_coluna(
    "municipio",
    precisa_codigo=True
)

col_ano = encontrar_coluna(
    "ano",
    precisa_codigo=True
)


print("\nColuna código município:")
print(
    col_codigo_municipio
)

print("\nColuna ano:")
print(
    col_ano
)


if col_codigo_municipio is None:
    raise ValueError(
        "Não foi possível identificar "
        "a coluna de município."
    )

if col_ano is None:
    raise ValueError(
        "Não foi possível identificar "
        "a coluna de ano."
    )


# ============================================================
# 6. DATAFRAME SIDRA
# ============================================================

estimativas = pd.DataFrame(
    dados[1:]
)


estimativas = estimativas[
    [
        col_codigo_municipio,
        col_ano,
        "V",
    ]
].copy()


estimativas = estimativas.rename(
    columns={
        col_codigo_municipio:
            "codigo_ibge",

        col_ano:
            "ano",

        "V":
            "populacao_referencia",
    }
)


# ============================================================
# 7. TIPOS
# ============================================================

estimativas[
    "codigo_ibge"
] = pd.to_numeric(
    estimativas[
        "codigo_ibge"
    ],
    errors="coerce"
)


estimativas[
    "ano"
] = pd.to_numeric(
    estimativas[
        "ano"
    ],
    errors="coerce"
)


estimativas[
    "populacao_referencia"
] = pd.to_numeric(
    estimativas[
        "populacao_referencia"
    ],
    errors="coerce"
)


estimativas = estimativas.dropna()


estimativas[
    "codigo_ibge"
] = (
    estimativas[
        "codigo_ibge"
    ]
    .astype("int64")
)

estimativas[
    "ano"
] = (
    estimativas[
        "ano"
    ]
    .astype("int64")
)

estimativas[
    "populacao_referencia"
] = (
    estimativas[
        "populacao_referencia"
    ]
    .astype("int64")
)


# ============================================================
# 8. FILTRO ESTADO DE SÃO PAULO
# ============================================================

estimativas = estimativas[
    estimativas[
        "codigo_ibge"
    ]
    .astype(str)
    .str.startswith("35")
].copy()


estimativas[
    "ano_referencia_populacao"
] = estimativas[
    "ano"
]

estimativas[
    "tipo_populacao"
] = (
    "Estimativa populacional IBGE"
)


print("\n" + "=" * 60)
print("ESTIMATIVAS 2020-2021")
print("=" * 60)

print("\nDimensão:")
print(
    estimativas.shape
)

print("\nRegistros por ano:")

print(
    estimativas
    .groupby("ano")
    .size()
)

print("\nMunicípios por ano:")

print(
    estimativas
    .groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)


# ============================================================
# 9. CENSO 2022
# ============================================================

pop_2022 = pd.read_csv(
    POP_2022_FILE
)


pop_2022 = pop_2022[
    [
        "codigo_ibge",
        "populacao_2022",
    ]
].copy()


pop_2022 = pop_2022.rename(
    columns={
        "populacao_2022":
            "populacao_referencia"
    }
)


pop_2022[
    "ano"
] = 2022

pop_2022[
    "ano_referencia_populacao"
] = 2022

pop_2022[
    "tipo_populacao"
] = (
    "Censo Demografico 2022"
)


# ============================================================
# 10. REFERÊNCIA PARA 2023
# ============================================================

pop_2023 = (
    pop_2022.copy()
)


pop_2023[
    "ano"
] = 2023

pop_2023[
    "ano_referencia_populacao"
] = 2022

pop_2023[
    "tipo_populacao"
] = (
    "Censo 2022 usado como referencia para 2023"
)


# ============================================================
# 11. PAINEL POPULACIONAL
# ============================================================

populacao = pd.concat(
    [
        estimativas,
        pop_2022,
        pop_2023,
    ],
    ignore_index=True
)


# ============================================================
# 12. JUNTA NOME DO MUNICÍPIO
# ============================================================

populacao = populacao.merge(
    mapa,
    on="codigo_ibge",
    how="left",
    validate="many_to_one"
)


populacao = populacao[
    [
        "ano",
        "codigo_ibge",
        "municipio",
        "populacao_referencia",
        "ano_referencia_populacao",
        "tipo_populacao",
    ]
]


populacao = populacao.sort_values(
    [
        "codigo_ibge",
        "ano",
    ]
).reset_index(
    drop=True
)


# ============================================================
# 13. VALIDAÇÕES
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO DO PAINEL POPULACIONAL")
print("=" * 60)

print("\nDimensão:")
print(
    populacao.shape
)

print("\nRegistros por ano:")

print(
    populacao
    .groupby("ano")
    .size()
)

print("\nMunicípios por ano:")

print(
    populacao
    .groupby("ano")[
        "codigo_ibge"
    ]
    .nunique()
)


duplicidades = (
    populacao
    .duplicated(
        subset=[
            "codigo_ibge",
            "ano",
        ]
    )
    .sum()
)


print("\nDuplicidades:")
print(
    duplicidades
)


print("\nValores ausentes:")
print(
    populacao
    .isna()
    .sum()
)


if duplicidades != 0:

    raise ValueError(
        "Existem duplicidades "
        "Município + Ano."
    )


if len(populacao) != 2580:

    raise ValueError(
        f"Esperadas 2580 linhas, "
        f"encontradas {len(populacao)}."
    )


if (
    populacao[
        "populacao_referencia"
    ]
    .isna()
    .any()
):

    raise ValueError(
        "Existem populações ausentes."
    )


# ============================================================
# 14. RESUMO
# ============================================================

print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)

print(
    populacao
    .groupby(
        [
            "ano",
            "ano_referencia_populacao",
            "tipo_populacao",
        ]
    )
    .agg(
        municipios=(
            "codigo_ibge",
            "nunique"
        ),
        populacao_total=(
            "populacao_referencia",
            "sum"
        ),
    )
)


# ============================================================
# 15. EXEMPLO: BAURU
# ============================================================

print("\n" + "=" * 60)
print("EXEMPLO - BAURU")
print("=" * 60)

print(
    populacao[
        populacao[
            "municipio"
        ]
        .str.contains(
            "Bauru",
            case=False,
            na=False
        )
    ]
    .to_string(
        index=False
    )
)


# ============================================================
# 16. SALVAMENTO
# ============================================================

populacao.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 60)
print("ARQUIVO GERADO")
print("=" * 60)

print(
    OUTPUT_FILE
)

print("\nExiste?")
print(
    OUTPUT_FILE.exists()
)

print(
    "\nPainel populacional concluído."
)