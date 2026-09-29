# Observatório dos Municípios Paulistas

Projeto de Ciência de Dados desenvolvido como parte do meu processo de formação em Ciência de Dados, utilizando dados públicos oficiais para analisar características econômicas e do mercado de trabalho dos municípios do estado de São Paulo.

O projeto utiliza a metodologia **CRISP-DM (Cross-Industry Standard Process for Data Mining)** para organizar todas as etapas, desde a definição do problema até a análise, modelagem e apresentação dos resultados.

---

## Objetivo do projeto

O objetivo principal é investigar quais características econômicas, populacionais e setoriais estão associadas à geração de empregos formais nos municípios paulistas.

Além da análise dos dados, o projeto também tem como objetivo desenvolver e demonstrar competências práticas em:

* Python
* Pandas
* consumo de APIs
* manipulação e limpeza de dados
* integração de diferentes bases públicas
* análise exploratória de dados
* estatística aplicada
* visualização de dados
* feature engineering
* Machine Learning
* Git e GitHub
* documentação de projetos de dados

---

# Metodologia

O projeto será desenvolvido utilizando a metodologia **CRISP-DM**.

As etapas são:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment

O desenvolvimento será iterativo, permitindo retornar a etapas anteriores sempre que novas descobertas nos dados exigirem ajustes.

---

# 1. Business Understanding

## Problema

Os municípios do estado de São Paulo apresentam diferenças significativas em população, estrutura econômica, renda, atividade industrial, serviços e geração de empregos.

A proposta deste projeto é utilizar dados públicos para investigar essas diferenças e identificar quais características estão relacionadas ao desempenho do mercado de trabalho municipal.

---

## Pergunta principal

**Quais características econômicas e populacionais estão associadas à geração de empregos formais nos municípios do estado de São Paulo?**

---

## Perguntas analíticas

Durante o projeto serão investigadas perguntas como:

* Quais municípios mais geram empregos formais?
* Quais municípios apresentam maior geração de empregos proporcionalmente à população?
* Municípios com maior PIB per capita apresentam maior geração de empregos?
* Existe relação entre participação da indústria e geração de emprego?
* Municípios predominantemente voltados para serviços apresentam comportamento diferente dos municípios industriais?
* Quais municípios apresentam resultados muito acima ou abaixo do esperado?
* Existem grupos de municípios com características econômicas semelhantes?
* Como Bauru se posiciona em relação aos demais municípios paulistas?

---

## Escopo inicial

O projeto será iniciado utilizando dados dos municípios do estado de São Paulo.

A unidade principal de análise será:

**Município + Ano**

O código oficial do município fornecido pelo IBGE será utilizado como chave para integração das diferentes bases de dados.

---

## Fontes de dados previstas

As principais fontes públicas que poderão ser utilizadas são:

### IBGE

Dados relacionados a:

* municípios
* população
* PIB
* PIB per capita
* composição econômica
* indústria
* serviços
* agropecuária

### Novo CAGED

Dados relacionados ao mercado formal de trabalho:

* admissões
* desligamentos
* saldo de empregos
* setores econômicos

### SICONFI / Tesouro Nacional

Em etapas posteriores poderão ser utilizados dados relacionados a:

* receitas municipais
* despesas
* investimentos públicos

### INEP

Também poderão ser incorporados indicadores relacionados a:

* escolas
* matrículas
* estrutura educacional

---

## Variável de interesse

Uma das principais métricas do projeto será o saldo de empregos formais.

Além do valor absoluto, será criada uma métrica proporcional:

`saldo de empregos por 1.000 habitantes`

Essa transformação permitirá comparar municípios de tamanhos diferentes de maneira mais adequada.

---

## Hipóteses iniciais

Algumas hipóteses que serão investigadas:

**H1:** municípios com maior participação industrial podem apresentar maior geração de empregos formais.

**H2:** municípios com maior PIB per capita não necessariamente apresentam maior geração proporcional de empregos.

**H3:** municípios de tamanho semelhante podem apresentar estruturas econômicas e resultados de emprego bastante diferentes.

Essas hipóteses serão tratadas como pontos de investigação e não como conclusões antecipadas.

---

## Critérios de sucesso

O projeto será considerado bem-sucedido se for possível:

* coletar dados públicos de fontes oficiais;
* construir uma base municipal integrada;
* documentar e tratar problemas de qualidade dos dados;
* produzir análises exploratórias relevantes;
* criar indicadores comparáveis entre municípios;
* aplicar técnicas estatísticas;
* desenvolver pelo menos um modelo de Machine Learning;
* avaliar corretamente o desempenho do modelo;
* interpretar os resultados;
* criar visualizações compreensíveis;
* documentar todo o processo no GitHub.

---

# Estrutura inicial do projeto

```text
observatorio_municipios_sp/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│
├── outputs/
│   └── graficos/
│
├── README.md
├── requirements.txt
├── .gitignore
└── main.py
```

---

# Status do projeto

**Fase atual:** CRISP-DM 1 — Business Understanding

Próxima etapa:

**CRISP-DM 2 — Data Understanding**

A próxima fase será iniciada com a exploração das fontes de dados e coleta da lista oficial de municípios paulistas através da API do IBGE.
