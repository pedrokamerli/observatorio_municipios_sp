from pathlib import Path

import pandas as pd
import requests


# ============================================================
# 1. CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
)

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. API SIDRA - CENSO 2022
# ============================================================

URL = (
    "https://apisidra.ibge.gov.br/"
    "values/t/4709/n6/all/v/93/p/2022"
    "?formato=json"
)


# ============================================================
# 3. REQUISIÇÃO
# ============================================================

print("\nConsultando população municipal no SIDRA...")

resposta = requests.get(
    URL,
    timeout=60
)

print("\nStatus HTTP:")
print(resposta.status_code)

resposta.raise_for_status()


# ============================================================
# 4. CONVERSÃO DO JSON
# ============================================================

dados = resposta.json()

print("\nQuantidade de elementos retornados:")
print(len(dados))


# ============================================================
# 5. INSPEÇÃO DA RESPOSTA
# ============================================================

print("\nCabeçalho retornado pela API:")
print(dados[0])

print("\nPrimeiro registro:")
print(dados[1])

print("\nSegundo registro:")
print(dados[2])


# ============================================================
# 6. DATAFRAME BRUTO
# ============================================================

df = pd.DataFrame(
    dados[1:]
)

print("\nDimensão do DataFrame:")
print(df.shape)

print("\nColunas:")
print(df.columns.tolist())

print("\nPrimeiras linhas:")
print(
    df.head().to_string()
)
# ============================================================
# 7. SALVAMENTO DA BASE BRUTA
# ============================================================

arquivo_saida = (
    RAW_DIR
    / "ibge_populacao_2022.csv"
)

df.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo bruto salvo em:")
print(arquivo_saida)

print("\nArquivo criado?")
print(arquivo_saida.exists())