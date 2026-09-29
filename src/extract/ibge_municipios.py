from pathlib import Path

import pandas as pd
import requests


# ============================================================
# 1. CONFIGURAÇÃO DA API
# ============================================================

URL = (
    "https://servicodados.ibge.gov.br/api/v1/"
    "localidades/estados/35/municipios"
)


# ============================================================
# 2. CAMINHOS DO PROJETO
# ============================================================

# Este arquivo está em:
# observatorio_municipios_sp/src/extract/ibge_municipios.py
#
# parents[0] -> extract
# parents[1] -> src
# parents[2] -> raiz do projeto

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

# Cria a pasta caso ela não exista
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. VERIFICAÇÃO DOS CAMINHOS
# ============================================================

print("Diretório atual de execução:")
print(Path.cwd())

print("\nRaiz do projeto:")
print(PROJECT_ROOT)

print("\nDiretório dos dados brutos:")
print(RAW_DIR)


# ============================================================
# 4. REQUISIÇÃO PARA A API DO IBGE
# ============================================================

print("\nConsultando API do IBGE...")

resposta = requests.get(
    URL,
    timeout=30
)

# Interrompe o programa caso a API retorne erro HTTP
resposta.raise_for_status()

print("Requisição realizada com sucesso.")
print("Status HTTP:", resposta.status_code)


# ============================================================
# 5. CONVERSÃO DA RESPOSTA JSON
# ============================================================

dados = resposta.json()

print("\nTipo do objeto recebido:")
print(type(dados))

print("\nQuantidade de registros recebidos:")
print(len(dados))


# ============================================================
# 6. TRANSFORMAÇÃO EM DATAFRAME
# ============================================================

df = pd.json_normalize(dados)


# ============================================================
# 7. DATA UNDERSTANDING
# ============================================================

print("\nPrimeiras linhas do DataFrame:")
print(df.head())

print("\nDimensão do DataFrame:")
print(df.shape)

print("\nColunas disponíveis:")
print(df.columns.tolist())


# ============================================================
# 8. VALIDAÇÕES INICIAIS
# ============================================================

print("\nCódigo e nome dos primeiros municípios:")
print(
    df[
        ["id", "nome"]
    ].head()
)

print("\nQuantidade de códigos IBGE únicos:")
print(df["id"].nunique())

print("\nQuantidade de códigos IBGE duplicados:")
print(df["id"].duplicated().sum())

print("\nQuantidade de valores nulos por coluna:")
print(df.isnull().sum())


# ============================================================
# 9. SALVAMENTO DOS DADOS BRUTOS
# ============================================================

arquivo_saida = RAW_DIR / "ibge_municipios_sp.csv"

df.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. CONFIRMAÇÃO DO SALVAMENTO
# ============================================================

print("\nCSV salvo em:")
print(arquivo_saida)

print("\nArquivo criado com sucesso?")
print(arquivo_saida.exists())