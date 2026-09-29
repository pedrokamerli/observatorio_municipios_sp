# Observatório dos Municípios Paulistas

Projeto de Ciência de Dados desenvolvido para analisar a dinâmica econômica e do mercado de trabalho dos municípios do Estado de São Paulo.

O projeto utiliza dados públicos oficiais, construção de pipelines de dados, análise exploratória, engenharia de atributos e Machine Learning, seguindo a metodologia CRISP-DM.

---

## Objetivo

Investigar quais características econômicas dos municípios paulistas estão associadas à geração de empregos formais e explorar a capacidade de modelos de Machine Learning de estimar a evolução do saldo de empregos.

Entre as perguntas estudadas estão:

- Como PIB, PIB per capita e porte municipal se relacionam com a geração de empregos?
- Municípios pequenos e grandes apresentam comportamentos diferentes?
- O tamanho econômico explica o saldo absoluto de empregos?
- É possível prever o saldo de empregos do ano seguinte?
- A dinâmica anterior do mercado de trabalho ajuda a prever sua evolução futura?

---

## Metodologia

O projeto segue a metodologia CRISP-DM:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment

Atualmente o projeto encontra-se nas etapas de modelagem e avaliação.

---

## Fontes de dados

### IBGE

Dados utilizados:

- municípios do Estado de São Paulo;
- Produto Interno Bruto municipal;
- PIB per capita;
- Valor Adicionado Bruto por atividade econômica;
- população do Censo 2022.

A base de PIB disponível utilizada no projeto possui informações de 2010 a 2023.

Para 2022 e 2023, os componentes setoriais de Valor Adicionado Bruto não estão disponíveis na mesma publicação utilizada, portanto não são imputados artificialmente.

### Novo CAGED

Microdados do Novo CAGED, disponibilizados pelo Ministério do Trabalho e Emprego.

Foram processadas todas as competências mensais entre:

- 2020
- 2021
- 2022
- 2023

Os arquivos originais possuem milhões de registros mensais e foram agregados por município.

---

## Pipeline do Novo CAGED

O projeto possui processo automatizado para:

1. conexão ao servidor de microdados;
2. download dos arquivos compactados;
3. extração dos arquivos TXT;
4. leitura otimizada das colunas necessárias;
5. filtro do Estado de São Paulo;
6. identificação de admissões e desligamentos;
7. agregação por município;
8. conversão do código CAGED para código IBGE por tabela de correspondência;
9. reconstrução do painel completo município × mês;
10. validações matemáticas;
11. agregação anual.

O painel mensal final possui:

```text
645 municípios
× 12 meses
× 4 anos
= 30.960 registros