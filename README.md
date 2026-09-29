# Observatório dos Municípios Paulistas

Projeto de Ciência de Dados voltado à análise econômica e do mercado de trabalho dos 645 municípios do Estado de São Paulo.

O projeto integra dados públicos do IBGE e do Novo CAGED, constrói pipelines de coleta e transformação, realiza análise exploratória, engenharia de atributos e experimentos de Machine Learning com avaliação temporal.

A proposta final é evoluir essa base para um **Observatório dos Municípios Paulistas**, permitindo analisar, comparar e acompanhar a trajetória econômica dos municípios ao longo do tempo.

---

## Visão do projeto

Este projeto não foi criado apenas para treinar modelos de Machine Learning.

A proposta é construir progressivamente uma plataforma analítica baseada em dados públicos capaz de integrar informações econômicas, demográficas e do mercado de trabalho dos municípios paulistas.

O projeto busca transformar diferentes fontes de dados em um painel longitudinal municipal que permita:

- acompanhar a evolução econômica dos municípios;
- analisar admissões, desligamentos e saldo de empregos;
- estudar PIB e PIB per capita;
- analisar características da estrutura econômica municipal;
- comparar municípios de diferentes portes;
- criar indicadores normalizados por população;
- identificar comportamentos atípicos;
- estudar relações temporais entre economia e emprego;
- desenvolver modelos preditivos;
- analisar onde e por que os modelos erram;
- comparar municípios com características semelhantes;
- disponibilizar futuramente os resultados em uma aplicação interativa.

A principal unidade de análise do projeto é:

```text
município + ano
```

Isso permite acompanhar cada município ao longo do tempo, evitando trabalhar apenas com fotografias isoladas de determinado período.

Exemplo conceitual:

```text
Bauru | 2020 | população | PIB | emprego | estrutura econômica
Bauru | 2021 | população | PIB | emprego | estrutura econômica
Bauru | 2022 | população | PIB | emprego | estrutura econômica
Bauru | 2023 | população | PIB | emprego | estrutura econômica
```

---

# Objetivo

Investigar características econômicas e do mercado de trabalho dos municípios paulistas e estudar quais fatores apresentam associação com a geração de empregos formais.

O projeto também investiga se informações econômicas e históricas de determinado município podem ajudar a estimar o comportamento do mercado de trabalho no período seguinte.

Entre as perguntas estudadas estão:

- Como PIB e PIB per capita se relacionam com geração de empregos?
- Qual é o impacto do porte municipal sobre os números absolutos de emprego?
- Municípios pequenos e grandes apresentam comportamentos diferentes?
- A geração relativa de empregos apresenta relação com tamanho econômico?
- O comportamento do mercado de trabalho de um ano ajuda a prever o ano seguinte?
- Crescimento econômico ajuda a prever mudanças no saldo de empregos?
- A estrutura econômica municipal ajuda a explicar diferenças entre municípios?
- Quais municípios apresentam comportamento muito diferente do esperado pelos modelos?

---

# Metodologia

O projeto utiliza como referência a metodologia **CRISP-DM**.

As etapas consideradas são:

```text
1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment
```

O desenvolvimento é incremental.

Cada etapa de modelagem parte dos resultados encontrados anteriormente. Quando um modelo apresenta limitações, o problema é reformulado antes da criação de modelos mais complexos.

Atualmente o projeto encontra-se principalmente nas etapas de:

```text
Modeling
+
Evaluation
```

com novas etapas de Data Preparation sendo adicionadas conforme novas fontes entram no painel.

---

# Fontes de dados

## IBGE

O projeto utiliza dados públicos disponibilizados pelo Instituto Brasileiro de Geografia e Estatística.

Entre os dados já utilizados estão:

- municípios do Estado de São Paulo;
- códigos oficiais dos municípios;
- Produto Interno Bruto municipal;
- PIB per capita;
- Valor Adicionado Bruto agropecuário;
- Valor Adicionado Bruto industrial;
- Valor Adicionado Bruto de serviços;
- Valor Adicionado Bruto da administração pública;
- população do Censo 2022.

A base municipal de PIB utilizada no projeto possui informações entre 2010 e 2023.

Para 2022 e 2023, os componentes de Valor Adicionado Bruto não estão disponíveis na mesma publicação utilizada no projeto.

Esses valores não são preenchidos artificialmente.

---

## Novo CAGED

O projeto também utiliza os microdados do Novo CAGED disponibilizados pelo Ministério do Trabalho e Emprego.

Foram processadas todas as competências mensais entre:

```text
2020
2021
2022
2023
```

Os arquivos originais possuem milhões de registros de movimentações trabalhistas.

O pipeline desenvolvido reduz esses microdados para indicadores municipais de:

```text
admissões
desligamentos
saldo de empregos
```

---

# Pipeline de dados

O fluxo geral do projeto é:

```text
IBGE
  ↓
Extração
  ↓
Transformação
  ↓
Validação
  ↓
Painel econômico
          ↑
Novo CAGED
  ↓
Download automático
  ↓
Extração dos arquivos
  ↓
Processamento mensal
  ↓
Agregação municipal
  ↓
Painel anual
```

As bases são integradas principalmente utilizando:

```text
codigo_ibge + ano
```

---

# Pipeline do Novo CAGED

Foi desenvolvido um processo automatizado para:

1. conectar ao servidor de microdados;
2. localizar as competências mensais;
3. baixar os arquivos compactados;
4. extrair os arquivos TXT;
5. realizar leitura otimizada das colunas necessárias;
6. filtrar registros do Estado de São Paulo;
7. identificar admissões e desligamentos;
8. agregar movimentações por município;
9. converter o código do CAGED para código IBGE utilizando mapa de correspondência;
10. reconstruir o painel completo município × mês;
11. identificar municípios sem movimentação registrada em determinadas competências;
12. preencher apenas as combinações ausentes do painel com zero;
13. preservar uma flag indicando ausência de movimentação;
14. validar os totais de admissões, desligamentos e saldo;
15. gerar as bases mensais e anuais.

---

# Base mensal do Novo CAGED

O painel mensal consolidado possui:

```text
645 municípios
×
12 meses
×
4 anos
=
30.960 observações
```

Não existem duplicidades na chave:

```text
codigo_ibge + ano + mes
```

---

# Base anual do Novo CAGED

Após a agregação mensal, foi criado um painel anual com:

```text
645 municípios
×
4 anos
=
2.580 observações
```

Não existem duplicidades na chave:

```text
codigo_ibge + ano
```

---

# Resultado agregado do Novo CAGED

| Ano | Admissões | Desligamentos | Saldo |
|---|---:|---:|---:|
| 2020 | 4.612.212 | 4.647.908 | -35.696 |
| 2021 | 6.136.283 | 5.334.294 | 801.989 |
| 2022 | 6.881.631 | 6.307.609 | 574.022 |
| 2023 | 7.113.110 | 6.727.614 | 385.496 |

Os dados mostram comportamentos bastante diferentes ao longo do período, incluindo saldo negativo em 2020 e forte recuperação em 2021.

---

# Painel econômico

As bases do IBGE e do Novo CAGED foram integradas utilizando:

```text
codigo_ibge + ano
```

O painel econômico atual contém:

```text
645 municípios
×
4 anos
=
2.580 observações
```

Entre as principais variáveis estão:

- PIB;
- PIB per capita;
- VAB agropecuário;
- VAB industrial;
- VAB de serviços;
- VAB da administração pública;
- admissões;
- desligamentos;
- saldo de empregos;
- crescimento do PIB;
- crescimento do PIB per capita;
- saldo de empregos do ano anterior;
- admissões do ano anterior;
- desligamentos do ano anterior;
- saldo de empregos do ano seguinte.

---

# Engenharia de atributos

Além das variáveis originais, o projeto começou a construir variáveis derivadas para representar melhor a dinâmica econômica dos municípios.

Entre elas:

```text
crescimento do PIB
crescimento do PIB per capita

saldo do ano anterior
admissões do ano anterior
desligamentos do ano anterior

total de movimentações

razão entre admissões e desligamentos

saldo sobre movimentações
```

O objetivo não é apenas fornecer mais variáveis aos modelos, mas representar melhor a evolução temporal do mercado de trabalho.

---

# Análise exploratória

A primeira análise detalhada foi realizada utilizando os dados de 2023.

A análise mostrou uma forte relação entre porte municipal e saldo absoluto de empregos.

Municípios maiores naturalmente apresentam:

```text
mais admissões
mais desligamentos
maiores saldos absolutos
```

Entretanto, ao normalizar o saldo pela população, essa associação cai consideravelmente.

Isso indica que o tamanho municipal explica grande parte do volume absoluto das movimentações trabalhistas, mas explica muito menos a geração relativa de empregos.

---

## Indicadores normalizados

Utilizando população do Censo 2022, foram criados inicialmente indicadores como:

```text
admissões por 1.000 habitantes

desligamentos por 1.000 habitantes

saldo de empregos por 1.000 habitantes
```

Esses indicadores permitiram comparar municípios com escalas muito diferentes.

A análise identificou pequenos municípios apresentando valores relativos bastante elevados ou bastante negativos.

Também foi observada maior dispersão das taxas entre municípios de pequeno porte.

---

# Correlação e escala

A análise exploratória mostrou que o saldo absoluto de empregos apresenta forte relação com variáveis de escala municipal.

Já o saldo normalizado por população apresenta relações muito menores com população e PIB absoluto.

Isso motivou duas decisões importantes:

```text
1. trabalhar com dimensão temporal;

2. desenvolver modelos utilizando indicadores normalizados.
```

---

# Machine Learning

## Problema inicial

O primeiro problema de Machine Learning foi estruturado como uma tarefa de regressão supervisionada.

A pergunta foi:

> Utilizando informações econômicas e trabalhistas disponíveis em determinado ano, é possível estimar o saldo de empregos do município no ano seguinte?

A avaliação respeita a ordem temporal dos dados.

Não foi utilizado:

```python
train_test_split(random_state=42)
```

com mistura aleatória de anos.

Isso evita que informações futuras contaminem o treinamento.

---

# Modelo Macro 01

O primeiro experimento tentou prever diretamente:

```text
saldo de empregos do próximo ano
```

A estrutura temporal foi:

```text
2020 → prever 2021
2021 → prever 2022

TREINO

2022 → prever 2023

TESTE
```

As primeiras variáveis utilizadas foram:

```text
PIB
PIB per capita
admissões
desligamentos
saldo atual
```

Foram avaliados:

```text
Baseline temporal
Regressão Linear
Ridge
Random Forest
```

---

## Resultados do Modelo Macro 01

| Modelo | MAE | RMSE | R² |
|---|---:|---:|---:|
| Baseline | 469,49 | 2.864,61 | 0,7247 |
| Random Forest | 706,42 | 3.346,40 | 0,6243 |
| Regressão Linear | 797,63 | 6.354,47 | -0,3547 |
| Ridge | 797,89 | 6.349,38 | -0,3525 |

O resultado mais importante do primeiro experimento foi que o baseline temporal apresentou desempenho superior aos modelos supervisionados.

O baseline utilizado foi:

```text
saldo futuro previsto =
saldo atual
```

Esse resultado mostrou que o histórico recente do próprio mercado de trabalho possui forte capacidade preditiva.

Também mostrou que simplesmente utilizar algoritmos mais complexos não garante melhores previsões.

---

# Diagnóstico do Modelo Macro 01

Os maiores erros da Random Forest ocorreram principalmente em grandes centros econômicos.

Entre os casos observados estavam municípios como:

```text
Campinas
Barueri
Osasco
Guarulhos
São Paulo
São Bernardo do Campo
Ribeirão Preto
Sorocaba
```

Isso indicou que o modelo estava aprendendo fortemente relações relacionadas à escala econômica.

Municípios com:

```text
PIB elevado
+
grande volume de admissões
+
grande volume de desligamentos
```

tendiam a receber previsões de saldo elevado.

Esse diagnóstico levou à reformulação do problema.

---

# Modelo Macro 02

Em vez de tentar prever diretamente o saldo futuro, o segundo experimento passou a prever:

```text
variação do saldo =
saldo do próximo ano - saldo atual
```

Assim, o modelo passou a tentar aprender a **mudança do mercado de trabalho**, e não apenas sua escala.

---

## Feature engineering do Modelo 02

Foram incorporadas variáveis como:

```text
crescimento do PIB

crescimento do PIB per capita

saldo do ano anterior

admissões do ano anterior

desligamentos do ano anterior

total de movimentações

razão entre admissões e desligamentos

saldo sobre movimentações
```

---

## Divisão temporal do Modelo 02

Como algumas features dependem do ano anterior, 2020 não possui todos os atributos históricos necessários.

A divisão ficou:

```text
TREINO

2021
↓
prever mudança até 2022


TESTE

2022
↓
prever mudança até 2023
```

O conjunto de treinamento possui:

```text
645 municípios
```

e o conjunto de teste também possui:

```text
645 municípios
```

---

# Resultados do Modelo Macro 02

## Previsão do saldo futuro reconstruído

| Modelo | MAE | RMSE | R² |
|---|---:|---:|---:|
| Ridge | 370,15 | 2.075,79 | 0,8554 |
| Random Forest | 384,49 | 1.794,85 | 0,8919 |
| Baseline | 469,49 | 2.864,61 | 0,7247 |
| Regressão Linear | 630,64 | 3.628,71 | 0,5582 |

O Modelo Macro 02 conseguiu superar o baseline.

O Ridge apresentou o menor erro absoluto médio:

```text
MAE = 370,15
```

contra:

```text
MAE baseline = 469,49
```

Isso representa redução de aproximadamente:

```text
21%
```

no erro absoluto médio.

A Random Forest apresentou:

```text
RMSE = 1.794,85
R² = 0,8919
```

indicando redução dos grandes erros e maior capacidade de explicar a variabilidade do saldo futuro.

---

# Importância das variáveis

Na Random Forest do Modelo Macro 02, a maior importância foi atribuída ao saldo de empregos do ano atual.

A ordem observada começou por:

```text
saldo atual

PIB

saldo do ano anterior

admissões

desligamentos

admissões anteriores

desligamentos anteriores
```

O saldo atual apresentou importância muito superior às demais variáveis.

Isso reforça a existência de forte persistência temporal no mercado de trabalho municipal.

Entretanto:

> importância de variável não representa causalidade.

O resultado deve ser interpretado apenas como contribuição da variável para as decisões realizadas pelo modelo.

---

# Aprendizados da modelagem

A evolução entre os dois primeiros modelos foi:

```text
MODELO 01

previsão direta do saldo
↓
modelos supervisionados perderam para o baseline


DIAGNÓSTICO

forte efeito de escala
+
forte persistência temporal


MODELO 02

previsão da variação do saldo
+
feature engineering temporal
↓
modelos conseguiram superar o baseline
```

Esse processo faz parte da metodologia do projeto.

O objetivo não é simplesmente aumentar a complexidade dos algoritmos, mas utilizar os resultados de cada experimento para melhorar a formulação do problema.

---

# Próximo experimento: Modelo Macro 03

O próximo passo será incorporar população municipal anual ao painel.

Hoje o projeto possui população do Censo 2022.

Para análises temporais, será necessário trabalhar com população correspondente aos diferentes períodos.

O objetivo será construir indicadores como:

```text
admissões por 1.000 habitantes

desligamentos por 1.000 habitantes

saldo por 1.000 habitantes

movimentações por 1.000 habitantes

saldo anterior por 1.000 habitantes
```

O Modelo Macro 03 deverá trabalhar com indicadores normalizados, reduzindo o efeito das diferenças de escala entre municípios como:

```text
São Paulo
Campinas
Guarulhos
Bauru
Lins
Cafelândia
```

---

# Análise setorial

Outra etapa prevista utiliza os componentes do Valor Adicionado Bruto.

Será possível construir variáveis como:

```text
participação da agropecuária no PIB

participação da indústria no PIB

participação dos serviços no PIB

participação da administração pública no PIB
```

Exemplo:

```text
participacao_industria =
VAB_industria / PIB
```

Isso permitirá investigar questões como:

```text
Municípios mais industriais apresentam dinâmica de emprego diferente?

Municípios mais dependentes de serviços apresentam maior ou menor estabilidade?

Municípios com maior participação agropecuária possuem comportamento distinto?

A estrutura econômica ajuda a explicar diferenças que o PIB total não explica?
```

Essa análise deverá respeitar a disponibilidade temporal das informações setoriais.

---

# Análise de resíduos

Depois dos modelos normalizados, o projeto deverá investigar os erros das previsões.

O objetivo será identificar municípios onde ocorreu algo como:

```text
previsão do modelo: +3.000 empregos

resultado observado: -500 empregos
```

Esses casos não serão automaticamente interpretados como falha dos dados.

Eles poderão indicar municípios cujo comportamento econômico foi diferente dos padrões aprendidos pelo modelo.

Esses municípios poderão ser utilizados como estudos de caso.

---

# Produto final pretendido

A evolução final do projeto deverá resultar em um **Observatório dos Municípios Paulistas**.

A proposta é permitir selecionar um município e visualizar indicadores como:

```text
Município: Bauru

População

PIB

PIB per capita

crescimento econômico

admissões

desligamentos

saldo de empregos

saldo por 1.000 habitantes

estrutura econômica

evolução histórica

comparação com municípios semelhantes

resultado observado

resultado estimado pelo modelo
```

---

# Comparação entre municípios

A aplicação também deverá permitir comparar municípios.

Exemplo:

```text
Bauru
Lins
Cafelândia
Jaú
```

com indicadores apresentados na mesma escala e ao longo do tempo.

---

# Estrutura do projeto

```text
observatorio_municipios_sp/
│
├── data/
│   │
│   ├── raw/
│   │   │
│   │   ├── caged/
│   │   │   ├── 2020/
│   │   │   ├── 2021/
│   │   │   ├── 2022/
│   │   │   └── 2023/
│   │   │
│   │   ├── ibge_municipios_sp.csv
│   │   ├── ibge_populacao_2022.csv
│   │   └── pib_municipios_ibge.xlsx
│   │
│   └── processed/
│       │
│       ├── mapa_municipios_sp.csv
│       ├── ibge_pib_sp.csv
│       ├── ibge_populacao_sp_2022.csv
│       │
│       ├── caged_sp_mensal_2020_2023.csv
│       ├── caged_sp_anual_2020_2023.csv
│       │
│       ├── base_analitica_sp_2023.csv
│       ├── base_analitica_sp_2023_com_populacao.csv
│       └── base_painel_sp_2020_2023.csv
│
├── outputs/
│   │
│   ├── graficos/
│   │   └── 2023/
│   │
│   └── modelos/
│       ├── comparacao_modelos_macro_01.csv
│       ├── previsoes_2023_macro_01.csv
│       ├── importancia_variaveis_rf_macro_01.csv
│       │
│       ├── comparacao_modelos_macro_02.csv
│       ├── previsoes_2023_macro_02.csv
│       └── importancia_variaveis_rf_macro_02.csv
│
├── src/
│   │
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── download_caged.py
│   │   ├── download_caged_multianual.py
│   │   ├── ibge_municipios.py
│   │   ├── ibge_pib.py
│   │   └── ibge_populacao.py
│   │
│   ├── transform/
│   │   ├── __init__.py
│   │   ├── mapa_municipios.py
│   │   ├── ibge_pib.py
│   │   ├── ibge_populacao.py
│   │   ├── integrar_populacao.py
│   │   ├── caged_mensal.py
│   │   ├── caged_anual.py
│   │   ├── caged_multianual.py
│   │   ├── base_analitica.py
│   │   └── base_painel_2020_2023.py
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── eda_2023.py
│   │   ├── eda_robusta_2023.py
│   │   └── graficos_eda_2023.py
│   │
│   └── modeling/
│       ├── __init__.py
│       ├── modelo_macro_01.py
│       └── modelo_macro_02.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── main.py
```

---

# Tecnologias utilizadas

```text
Python
Pandas
NumPy
Scikit-learn
Matplotlib
Requests
Py7zr
OpenPyXL
Git
GitHub
```

---

# Como executar o projeto

Crie ou ative um ambiente virtual Python.

Instale as dependências:

```bash
pip install -r requirements.txt
```

Os scripts estão separados pelas responsabilidades:

```text
src/extract/
→ coleta e download de dados

src/transform/
→ limpeza, transformação, integração e criação dos painéis

src/analysis/
→ análise exploratória e visualizações

src/modeling/
→ experimentos de Machine Learning
```

---

# Dados brutos

Os microdados do Novo CAGED possuem arquivos muito grandes.

Por esse motivo, os arquivos brutos e algumas bases processadas podem não estar versionados diretamente no GitHub.

O código necessário para reconstruir as bases faz parte do projeto.

---

# Estado atual do projeto

```text
Coleta IBGE                         ✅

Processamento PIB                   ✅

Coleta Novo CAGED                   ✅

Automação de download               ✅

CAGED mensal 2020–2023              ✅

CAGED anual 2020–2023               ✅

Mapa CAGED → IBGE                   ✅

Integração IBGE + CAGED             ✅

Painel econômico                    ✅

EDA 2023                            ✅

Análise robusta                     ✅

Indicadores relativos iniciais      ✅

Modelo Macro 01                     ✅

Feature engineering temporal        ✅

Modelo Macro 02                     ✅

População anual 2020–2023           ⏳

Modelo Macro 03 normalizado         ⏳

Análise de resíduos                 ⏳

Análise setorial                    ⏳

Comparação final dos modelos        ⏳

Dashboard / Observatório            ⏳
```

---

# Próximas etapas

A próxima etapa técnica do projeto será incorporar população municipal anual ao painel 2020–2023.

Depois disso:

```text
População anual
        ↓
Indicadores por 1.000 habitantes
        ↓
Modelo Macro 03
        ↓
Análise de resíduos
        ↓
Análise setorial
        ↓
Comparação dos modelos
        ↓
Visualizações finais
        ↓
Observatório interativo
```

---

# Limitações atuais

O projeto ainda possui algumas limitações importantes.

O histórico do Novo CAGED utilizado para modelagem neste estágio cobre apenas 2020 a 2023.

Isso reduz a quantidade de períodos disponíveis para treinamento temporal.

O Modelo Macro 02, por exemplo, possui apenas um ano completo como conjunto de treinamento depois da criação dos lags necessários.

Portanto, os resultados atuais devem ser tratados como experimentos exploratórios de Machine Learning e não como um sistema de previsão operacional.

Outra limitação está relacionada aos dados setoriais do PIB.

Os componentes de Valor Adicionado Bruto não estão disponíveis para todos os anos mais recentes da publicação utilizada.

Esses dados não serão artificialmente imputados apenas para aumentar a quantidade de features.

---

# Cuidados metodológicos

Os modelos deste projeto buscam identificar padrões estatísticos.

Os resultados não devem ser interpretados automaticamente como relações causais.

Por exemplo:

```text
PIB associado a emprego
```

não significa necessariamente:

```text
aumento do PIB causou diretamente aumento do emprego.
```

Da mesma forma:

```text
feature importance
```

indica importância para o modelo, e não importância causal para a economia do município.

---

# Evolução do projeto

O projeto foi desenvolvido de forma incremental.

A sequência principal até o momento foi:

```text
dados públicos
↓
coleta
↓
limpeza
↓
validação
↓
integração
↓
painel longitudinal
↓
EDA
↓
diagnóstico
↓
Machine Learning
↓
avaliação
↓
reformulação do problema
↓
novo experimento
```

Esse processo é parte importante do projeto.

O objetivo não é apenas obter uma métrica alta, mas compreender como os dados, as variáveis e a formulação do problema afetam os resultados.

---

# Objetivo final

O objetivo final é transformar o projeto em uma ferramenta analítica capaz de responder perguntas sobre a evolução econômica dos municípios paulistas.

Mais do que prever números, a proposta é oferecer uma estrutura para:

```text
entender
comparar
investigar
visualizar
modelar
```

a dinâmica econômica municipal utilizando dados públicos reproduzíveis.

---

# Autor

**Pedro Merli**

Projeto desenvolvido como estudo prático de:

```text
Ciência de Dados
Engenharia de Dados
Análise de Dados Públicos
Machine Learning
Estatística
Visualização de Dados
Git e versionamento
```