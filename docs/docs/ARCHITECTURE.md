# Documentação da Arquitetura

## 1. Objetivo

Este documento descreve a arquitetura do projeto **Book Recommendation Data API**, focando nas decisões arquiteturais, no fluxo de dados ponta a ponta, na preparação para escalabilidade futura e na integração com modelos de Machine Learning.

Detalhes operacionais, instruções de execução, exemplos de uso da API e orientações para desenvolvedores estão intencionalmente fora deste documento e são tratados no arquivo `README.md`.

## 2. Visão Geral da Arquitetura

A arquitetura foi pensada com uma abordagem **data-first**, priorizando a estruturação e a disponibilização de dados antes da implementação de modelos de recomendação. 

O sistema segue um pipeline organizado da seguinte forma:

**Ingestão → Processamento → Armazenamento → API → Consumo**

Cada etapa é tratada isoladamente, permitindo evolução independente, substituição tecnológica e escalabilidade progressiva sem impacto direto nas demais etapas.

Essa separação garante que o projeto possa evoluir de uma solução simples para uma plataforma de dados e Machine Learning mais robusta ao longo do tempo.

---

## 3. Pipeline de Dados de Ponta a Ponta

### 3.1 Ingestão de Dados

A camada de ingestão é responsável por coletar dados de livros a partir de fontes externas públicas (Books to Scrape), através de técnicas de web scraping.

Principais características dessa etapa:

- Executada de forma independente da API
- Não depende de requisições de usuários finais
- Pode ser acionada manualmente ou por agendamento
- Preparada para suportar múltiplas fontes no futuro

A decisão de desagregar a ingestão da API evita sobrecarga no serviço de consumo e garante maior controle sobre a qualidade e a frequência de atualização dos dados.

---

### 3.2 Processamento e Normalização

Após a ingestão, os dados brutos passam por uma etapa de processamento responsável por:

- Limpeza de dados inconsistentes ou incompletos
- Padronização de campos (autores, categorias)
- Normalização estrutural do dataset
- Validação básica de integridade

Nesta fase, optamos por aplicar **apenas transformações essenciais**, evitando engenharia de atributos antecipada. Essa decisão preserva a flexibilidade analítica para cientistas de dados e engenheiros de Machine Learning, que poderão definir transformações específicas conforme o modelo utilizado.

---

### 3.3 Armazenamento de Dados

Os dados processados são armazenados em um formato CSV adequado para consumo analítico e treinamento de modelos de Machine Learning. 

Características arquiteturais dessa camada:

- Estrutura desacoplada da API
- Formato substituível
- Possibilidade de evolução tecnológica

Inicialmente, o armazenamento pode ser simples (ex.: arquivos estruturados), mas a arquitetura permite migração futura para bancos relacionais, NoSQL ou data warehouses sem impacto direto nas camadas superiores.

---

### 3.4 Exposição via API

A API atua exclusivamente como uma **camada de acesso aos dados**, funcionando como conexão entre o pipeline de dados e os consumidores.

Decisões arquiteturais importantes:

- A API é stateless
- Não realiza processamento pesado
- Não executa lógica de Machine Learning
- Apenas consulta e entrega dados estruturados

Essa estrutura permite que a API seja escalada horizontalmente e versionada sem afetar o pipeline de ingestão ou processamento.

---

### 3.5 Consumo dos Dados

Os dados disponibilizados pela API podem ser consumidos por diferentes perfis:

- Cientistas de dados
- Engenheiros de Machine Learning
- Sistemas externos
- Pipelines analíticos

A API elimina a necessidade de scraping direto por consumidores, centralizando a responsabilidade de coleta e padronização dos dados.

---

## 4. Arquitetura Orientada à Escalabilidade

### 4.1 Princípios Arquiteturais

A arquitetura foi desenhada considerando evolução incremental, evitando refatorações significativas no futuro.

Os principais princípios adotados são:

- Camadas desacopladas
- Separação entre dados, API e modelos
- Independência tecnológica entre componentes
- Evolução progressiva do pipeline 

---

### 4.2 Escalabilidade por Camada

#### Ingestão

- Evolução para execução paralela
- Inclusão de novas fontes de dados
- Possibilidade de agendamento automático

#### Processamento

- Migração para pipelines distribuídos
- Suporte a processamento em batch ou streaming
- Possibilidade de validações mais avançadas

#### Armazenamento

- Migração para bancos de dados escaláveis
- Separação entre dados operacionais e analíticos
- Suporte a grande volume de dados

#### API

- Escala horizontal com balanceamento de carga
- Versionamento de endpoints
- Controle de acesso e autenticação

---

## 5. Cenários de Uso para Dados e Machine Learning

### 5.1 Cientistas de Dados

- Exploração e análise dos dados
- Avaliação de qualidade e consistência
- Criação de datasets para treinamento e validação
- Experimentação de estratégias de recomendação

---

### 5.2 Engenheiros de Machine Learning

- Consumo de dados padronizados para treinamento
- Reprodutibilidade de experimentos
- Integração com pipelines de Machine Learning
- Preparação para processamento em lote e serviço em tempo real 

---

### 5.3 Sistemas Externos

- Integração com sistemas de busca ou recomendação
- Consumo de dados estruturados via API
- Uso da API como serviço provedor de dados 

---


## 6. Plano de Integração com Machine Learning

### 6.1 Curto Prazo

- Uso da API para geração de datasets offline
- Implementação de modelos tradicionais de recomendação
- Avaliação de métricas básicas de desempenho
 
---


### 6.2 Médio Prazo

- Criação de endpoints especializados para features
- Geração de embeddings a partir de textos
- Suporte a múltiplas versões de datasets
- Experimentação com diferentes algoritmos

---

### 6.3 Longo Prazo

- Deploy de modelos como serviços independentes
- Integração de inferência online
- Introdução de feature stores
- Monitoramento de modelos e dados


---

## 7. Resumo das Decisões Arquiteturais


- Pipeline de dados definido antes dos modelos
- Transformações mínimas no estágio inicial
- Arquitetura preparada para evolução em ML
- Escalabilidade considerada desde o início

---
## 8. Diagrama de Arquitetura

```mermaid
flowchart LR
    A[Fonte Externa de Dados]
    B[Camada de Ingestão\nWeb Scraping]
    C[Processamento e Normalização]
    D[Armazenamento Estruturado]
    E[API REST]
    F[Consumidores de Dados]
    G[Modelos de Machine Learning]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
