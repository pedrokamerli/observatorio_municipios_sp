"""Aplicação Streamlit do Observatório dos Municípios Paulistas."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Observatório dos Municípios Paulistas", page_icon="📊", layout="wide")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARQUIVO = PROJECT_ROOT / "data" / "processed" / "base_observatorio_sp.csv"


@st.cache_data
def carregar_dados(caminho: str) -> pd.DataFrame:
    return pd.read_csv(caminho)


def numero(valor: float) -> str:
    return "N/D" if pd.isna(valor) else f"{valor:,.0f}".replace(",", ".")


def decimal(valor: float, casas: int = 2) -> str:
    return "N/D" if pd.isna(valor) else f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def moeda(valor: float, casas: int = 2) -> str:
    return "N/D" if pd.isna(valor) else f"R$ {decimal(valor, casas)}"


def ranking(valor: float) -> str:
    return "N/D" if pd.isna(valor) else f"{int(valor)}º de 645"


def tabela_formatada(dados: pd.DataFrame, colunas: dict[str, str]) -> pd.DataFrame:
    return dados[list(colunas)].rename(columns=colunas)


def grafico_linha(dados: pd.DataFrame, y: str, titulo: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(dados["ano"], dados[y], marker="o", color="#1f77b4")
    if dados[y].min() < 0:
        ax.axhline(0, linestyle="--", linewidth=1, color="#6c757d")
    ax.set(xlabel="Ano", ylabel=ylabel, title=titulo)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


if not ARQUIVO.exists():
    st.error("A base do Observatório não foi encontrada. Execute o pipeline de transformação antes de iniciar a aplicação.")
    st.stop()

df = carregar_dados(str(ARQUIVO))
municipios = sorted(df["municipio"].dropna().unique())
anos = sorted(df["ano"].dropna().unique(), reverse=True)

st.title("Observatório dos Municípios Paulistas")
st.caption("Indicadores econômicos e do mercado de trabalho dos 645 municípios do Estado de São Paulo, de 2020 a 2023.")

nomes_abas = ["Visão Estadual", "Município", "Comparar", "Metodologia"]
aba_inicial = st.query_params.get("aba", "Visão Estadual")
aba_inicial = aba_inicial if aba_inicial in nomes_abas else "Visão Estadual"
aba_estado, aba_municipio, aba_comparar, aba_metodologia = st.tabs(nomes_abas, default=aba_inicial)

with aba_estado:
    st.header("Visão Estadual")
    ano_estado = st.selectbox("Ano de referência", anos, key="ano_estado")
    estado = df[df["ano"] == ano_estado].copy()
    totais = estado[["populacao_referencia", "pib", "admissoes", "desligamentos", "saldo_empregos"]].sum()
    saldo_1000_estado = totais["saldo_empregos"] / totais["populacao_referencia"] * 1000
    st.caption("Os totais agregam os 645 municípios. PIB na base original do IBGE está em milhares de reais.")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Municípios", numero(estado["municipio"].nunique()))
    c2.metric("População de referência", numero(totais["populacao_referencia"]))
    c3.metric("PIB estadual", f"R$ {decimal(totais['pib'] / 1_000_000, 2)} tri")
    c4.metric("Saldo de empregos", numero(totais["saldo_empregos"]))
    c5.metric("Saldo / 1.000 hab.", decimal(saldo_1000_estado))
    historico_estado = df.groupby("ano", as_index=False).agg(populacao_referencia=("populacao_referencia", "sum"), pib=("pib", "sum"), admissoes=("admissoes", "sum"), desligamentos=("desligamentos", "sum"), saldo_empregos=("saldo_empregos", "sum"))
    historico_estado["saldo_por_1000_hab"] = historico_estado["saldo_empregos"] / historico_estado["populacao_referencia"] * 1000
    esquerda, direita = st.columns(2)
    with esquerda:
        grafico_linha(historico_estado, "saldo_empregos", "Evolução do saldo de empregos", "Saldo de empregos")
    with direita:
        grafico_linha(historico_estado, "pib", "Evolução do PIB estadual", "PIB (milhares de R$)")
    st.subheader(f"Destaques municipais — {ano_estado}")
    top_esquerda, top_direita = st.columns(2)
    with top_esquerda:
        st.caption("Maiores saldos absolutos de empregos")
        st.bar_chart(estado.nlargest(10, "saldo_empregos")[["municipio", "saldo_empregos"]].set_index("municipio"), horizontal=True)
    with top_direita:
        st.caption("Maiores saldos por 1.000 habitantes")
        st.bar_chart(estado.nlargest(10, "saldo_por_1000_hab")[["municipio", "saldo_por_1000_hab"]].set_index("municipio"), horizontal=True)
    st.subheader("Distribuição do saldo relativo")
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.hist(estado["saldo_por_1000_hab"].dropna(), bins=35, color="#1f77b4", edgecolor="white")
    ax.axvline(saldo_1000_estado, color="#d62728", linestyle="--", label="Média estadual ponderada")
    ax.set(xlabel="Saldo de empregos por 1.000 habitantes", ylabel="Número de municípios")
    ax.legend()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with aba_municipio:
    st.header("Consulta municipal")
    st.caption("Bauru é apenas o exemplo inicial da consulta; selecione qualquer município paulista.")
    indice_bauru = municipios.index("Bauru") if "Bauru" in municipios else 0
    selecao1, selecao2 = st.columns([2, 1])
    with selecao1:
        municipio_selecionado = st.selectbox("Município", municipios, index=indice_bauru)
    with selecao2:
        ano_selecionado = st.selectbox("Ano", anos, key="ano_municipio")
    historico = df[df["municipio"] == municipio_selecionado].sort_values("ano").copy()
    registro = historico[historico["ano"] == ano_selecionado].iloc[0]
    if ano_selecionado == 2023 and registro["ano_referencia_populacao"] == 2022:
        st.info("Para 2023, a população de referência é a do Censo Demográfico de 2022.")
    st.subheader(f"{municipio_selecionado} — {ano_selecionado}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("População de referência", numero(registro["populacao_referencia"]))
    c2.metric("PIB", moeda(registro["pib"] * 1000, 0))
    c3.metric("PIB per capita", moeda(registro["pib_per_capita"]))
    c4.metric("Saldo de empregos", numero(registro["saldo_empregos"]))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Admissões", numero(registro["admissoes"]))
    c2.metric("Desligamentos", numero(registro["desligamentos"]))
    c3.metric("Saldo / 1.000 hab.", decimal(registro["saldo_por_1000_hab"]))
    c4.metric("Movimentações / 1.000 hab.", decimal(registro["movimentacoes_por_1000_hab"]))
    st.subheader("Posição no Estado de São Paulo")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ranking PIB", ranking(registro["ranking_pib"]))
    c2.metric("Ranking PIB per capita", ranking(registro["ranking_pib_per_capita"]))
    c3.metric("Ranking saldo de empregos", ranking(registro["ranking_saldo_empregos"]))
    c4.metric("Ranking saldo / 1.000 hab.", ranking(registro["ranking_saldo_1000"]))
    st.subheader("Evolução histórica")
    esquerda, direita = st.columns(2)
    with esquerda:
        grafico_linha(historico, "pib_per_capita", f"PIB per capita — {municipio_selecionado}", "R$")
    with direita:
        grafico_linha(historico, "saldo_empregos", f"Saldo de empregos — {municipio_selecionado}", "Saldo de empregos")
    grafico_linha(historico, "saldo_por_1000_hab", f"Saldo relativo — {municipio_selecionado}", "Saldo por 1.000 habitantes")
    st.subheader("Estrutura econômica")
    if pd.notna(registro["setor_dominante"]):
        st.write(f"**Setor dominante:** {registro['setor_dominante']}")
        setores = pd.DataFrame({"Setor": ["Agropecuária", "Indústria", "Serviços", "Administração pública"], "Participação no PIB (%)": [registro["participacao_agro_pct"], registro["participacao_industria_pct"], registro["participacao_servicos_pct"], registro["participacao_adm_publica_pct"]]})
        st.bar_chart(setores.set_index("Setor"))
    else:
        st.info("Os componentes setoriais do VAB estão disponíveis somente para 2020 e 2021 nesta base.")
    if ano_selecionado == 2023:
        st.subheader("Experimento de Machine Learning")
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo observado", numero(registro["saldo_real_2023"]))
        c2.metric("Saldo estimado (Modelo 03)", numero(registro["modelo03_saldo_previsto"]))
        c3.metric("Erro absoluto", numero(registro["modelo03_erro_absoluto"]))
        st.caption("O Modelo 03 (Random Forest) é um experimento exploratório, não uma previsão operacional. A análise de resíduos indicou influência dos municípios de maior porte no desempenho agregado.")
    st.subheader("Histórico municipal")
    st.dataframe(tabela_formatada(historico, {"ano": "Ano", "populacao_referencia": "População", "pib_per_capita": "PIB per capita (R$)", "admissoes": "Admissões", "desligamentos": "Desligamentos", "saldo_empregos": "Saldo", "saldo_por_1000_hab": "Saldo / 1.000 hab."}), hide_index=True, width="stretch")

with aba_comparar:
    st.header("Comparar municípios")
    st.write("Selecione de dois a seis municípios para comparar indicadores econômicos e de emprego.")
    padrao = [nome for nome in ["Bauru", "Campinas", "Ribeirão Preto"] if nome in municipios]
    municipios_comparacao = st.multiselect("Municípios", municipios, default=padrao, max_selections=6)
    ano_comparacao = st.selectbox("Ano da comparação", anos, key="ano_comparacao")
    if len(municipios_comparacao) < 2:
        st.info("Selecione pelo menos dois municípios para realizar a comparação.")
    else:
        comparacao = df[(df["municipio"].isin(municipios_comparacao)) & (df["ano"] == ano_comparacao)].copy().sort_values("saldo_empregos", ascending=False)
        st.subheader(f"Indicadores — {ano_comparacao}")
        st.dataframe(tabela_formatada(comparacao, {"municipio": "Município", "populacao_referencia": "População", "pib_per_capita": "PIB per capita (R$)", "saldo_empregos": "Saldo", "saldo_por_1000_hab": "Saldo / 1.000 hab.", "ranking_saldo_empregos": "Ranking saldo"}), hide_index=True, width="stretch")
        esquerda, direita = st.columns(2)
        with esquerda:
            st.subheader("PIB per capita")
            st.bar_chart(comparacao.set_index("municipio")[["pib_per_capita"]], horizontal=True)
        with direita:
            st.subheader("Saldo de empregos")
            st.bar_chart(comparacao.set_index("municipio")[["saldo_empregos"]], horizontal=True)
        st.subheader("Evolução do saldo por 1.000 habitantes")
        st.line_chart(df[df["municipio"].isin(municipios_comparacao)].pivot(index="ano", columns="municipio", values="saldo_por_1000_hab"))

with aba_metodologia:
    st.header("Metodologia")
    st.markdown("""
### Fontes e unidade de análise
O Observatório integra dados públicos do **IBGE** e do **Novo CAGED / Ministério do Trabalho e Emprego**. A unidade de análise é **município + ano**, formando um painel com os **645 municípios paulistas entre 2020 e 2023**.

### Indicadores e comparabilidade
Os indicadores de emprego por 1.000 habitantes usam a população de referência disponível na base. Para 2023, utiliza-se o Censo Demográfico 2022. Os componentes setoriais do Valor Adicionado Bruto estão disponíveis somente para 2020 e 2021.

### Modelagem
Foram conduzidos quatro experimentos de Machine Learning. O **Modelo 03**, baseado em Random Forest, é o principal experimento: reduziu o MAE de 469,49 no baseline para 360,66, uma redução de **23,18%**. Seu R² agregado foi 0,9391, mas a análise de resíduos mostrou influência dos municípios de maior porte no desempenho agregado.

Os resultados são exploratórios. Correlação, importância de variáveis e estimativas do modelo não estabelecem causalidade nem constituem previsão operacional.
""")

st.divider()
st.caption("Observatório dos Municípios Paulistas • Projeto de Ciência de Dados • Fontes: IBGE e Novo CAGED")
