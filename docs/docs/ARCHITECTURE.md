# Documentação da Arquitetura

Este documento descreve a arquitetura do projeto **Book Recommendation Data API**, focando nas decisões de arquitetura, no fluxo de dados ponta a ponta, na preparação para escalabilidade futura e na integração com modelos de Machine Learning.

## 1. 🌐 Visão Geral
Book Sommelier API é uma plataforma construída com Python e Flask que realiza:
1. Coleta de dados por Web Scraping
2. Armazenamento dos livros em CSV e banco de dados
3. Exposição de uma API REST para consultas e análises
4. Preparação para pipelines de Machine Learning (recomendações, análises de preço, NLP etc.)

O projeto segue uma arquitetura organizada em Pipeline → API → Consumo permitindo fácil evolução e escalabilidade.

## 2. 🧩 Pipeline: Ingestão → Processamento → API → Consumo
O pipeline do Book Sommelier API garante a coleta, padronização, armazenamento e disponibilização dos dados de livros para aplicações, análises e modelos de machine learning. Ele é composto por quatro etapas, cada uma com responsabilidades bem definidas, componentes específicos e padrões arquiteturais próprios.
A seguir, cada etapa é descrita com o fluxo de dados.

🔵 2.1 Ingestão — Web Scraper (scripts/scraper.py)

A etapa de ingestão é responsável por capturar dados brutos diretamente da fonte externa (books.toscrape.com). Este é o ponto inicial do pipeline.

🎯 Responsabilidades da etapa de ingestão

O BookScraper executa um fluxo completo de extração:

*Descoberta da paginação*

- Acessa a primeira página do catálogo (page-1.html)
- Identifica o total de páginas via HTML (ul.pager)
- Registra last_page para controlar o loop de scraping

Isso permite navegar de forma dinâmica mesmo se o site aumentar/deixar de exibir produtos.

*Coleta de URLs individuais de livros*

Para cada página:
- Envia requisição HTTP com cabeçalho (User-Agent)
- Faz parsing do HTML com BeautifulSoup
- Extrai links relativos (href) de cada <article class="product_pod">

O resultado é uma lista _books_urls com todos os livros do site.

*Extração de metadados de cada livro*

Para cada URL individual, realiza: 
- Leitura da página detalhada do livro
- Extração dos campos: Título, Preço bruto, Moeda, Preço em centavos, RatingClasse, Categoria, URL da Imagem.

*Padronização e limpeza dos dados*

Antes da persistência:
- Conversão de moeda → currency code internacional
- Conversão de preços → inteiros em centavos
- Tratamento de campos opcionais (rating, img_url, category)
- Garantia de limpeza (strip(), validações básicas)

*Persistência via DataStorage*

O scraper é projetado para funcionar com qualquer mecanismo de persistência, por meio de uma interface externa (DataStorage). 
No projeto atual, usamos CSVWriter. 
Grava os dados estruturados em: /data/books.csv.

O CSV será o dataset usado pelas etapas posteriores.

Tecnologias utilizadas
- Requests → comunicação HTTP
- BeautifulSoup → parsing de HTML
- Regex → normalização de preço/moeda
- Pandas (indiretamente) → posteriormente usado na leitura do CSV

Resultado da Etapa

📄 data/books.csv

## 3. 🧬 Arquitetura de Escalabilidade Futura

A arquitetura do Book Sommelier API foi projetada pensando não apenas no funcionamento atual, mas também em sua evolução natural à medida que o volume de dados cresce, novos requisitos surgem e aplicações de machine learning passam a consumir os dados disponibilizados. O sistema adota uma postura modular, permitindo que cada parte da solução possa ser substituída, ampliada ou reorganizada sem a necessidade de reescrever o projeto do zero.

A seguir, descrevemos cada eixo de escalabilidade previsto no desenho arquitetural.

3.1 Escala Horizontal da API

A camada de API foi pensada para suportar o modelo de escalabilidade horizontal, no qual múltiplas instâncias da aplicação rodam simultaneamente para absorver picos de demanda.
Isso se torna possível graças ao empacotamento via Docker, que permite facilmente replicar o container da aplicação e executá-lo em diferentes provedores compatíveis com containers, como Render, Railway, Fly.io ou Kubernetes.
Uma vez que múltiplas instâncias estejam rodando, um load balancer pode distribuir requisições entre elas de maneira uniforme, garantindo:
- maior tolerância a falhas,
- maior disponibilidade,
- melhor desempenho,
- isolamento de workloads pesadas.

A arquitetura também permite configurar workers independentes para dividir tarefas de forma eficiente — por exemplo, servir requisições síncronas enquanto processos mais caros são tratados em paralelo.

3.2 Escalonamento do Pipeline

Hoje, o fluxo do pipeline é simples e sequencial: scraping → CSV → importação para o banco.
Essa estrutura é eficiente para pequenas e médias quantidades de dados, mas pode se tornar um gargalo à medida que novas fontes, volumes maiores ou múltiplos scrapers forem adicionados.
Para o futuro, o pipeline pode ser evoluído para um modelo distribuído e altamente escalável:
Scraper → FILA (Kafka/RabbitMQ) → Processador paralelo → Banco → API → ML

Nesse formato:
O Scraper envia mensagens para um barramento assíncrono (Kafka, RabbitMQ).
Consumidores paralelos processam cada item individualmente, permitindo ingestão massiva.
O banco é alimentado em fluxo contínuo.
A API passa a servir dados atualizados em tempo real.
Pipelines de ML recebem informações renovadas automaticamente.

Esse desenho suporta múltiplos scrapers, maior throughput e velocidades de ingestão muito superiores, deixando o sistema pronto para cenários de Big Data.

3.3 Migração de CSV para Data Lake

Embora o CSV seja ótimo para prototipagem, ele não escala bem quando surgem demandas relacionadas a:
- alta volumetria,
- versionamento de dados,
- consultas avançadas,
- integração com pipelines analíticos.

Por isso, prevê-se uma futura migração para formatos mais robustos como:
- Parquet (compacto, colunar, otimizado),
- ORC, ou mesmo para armazenamento distribuído como:
a. Amazon S3,
b. Google Cloud Storage,
c. MinIO (self-hosted S3).

Com isso, ferramentas como AWS Glue, Apache Spark ou Databricks podem processar grandes volumes em segundos, dando ao projeto um caminho claro para análises avançadas e engenharia de características para ML.

3.4 Cache em Camadas

Para evitar reprocessar consultas que mudam pouco (como top-rated, categorias ou estatísticas de overview), o sistema pode adicionar uma camada de cache como o Redis.
Isso permite:
- respostas quase instantâneas (milissegundos),
- menor carga no banco,
- escalabilidade mais barata,
- ótima performance para dashboards e consumidores repetitivos.

3.5 Observabilidade Completa

À medida que a aplicação cresce, torna-se essencial ter visibilidade clara de seu comportamento. A arquitetura prevê adição de: 
- logs estruturados em JSON (para análise no ELK/Datadog),
- Prometheus para coletar métricas (latência, erros, throughput),
- Grafana para dashboards e alertas,
- OpenTelemetry para rastreamento distribuído entre API, banco, scrapers e pipelines.

Com isso, qualquer anomalia é detectada rapidamente e as equipes conseguem observar o impacto de novas versões ou cargas elevadas.

## 4. 🧠 Cenário Real de Uso para Data Science & ML

A arquitetura foi desenhada para servir como uma base sólida para pipelines de machine learning. Ela disponibiliza dados limpos, consistentes e padronizados, facilitando tarefas como modelagem, previsão e geração de recomendações.
A seguir estão cenários reais de uso contemplados pela arquitetura.

4.1 Regressão de Preço

A API permite a criação de modelos que estimam o valor de um livro com base em múltiplas variáveis.
Um cientista de dados pode usar atributos como: rating numérico, categoria, tokens do título extraídos (TF-IDF, Bag-of-Words), características da imagem de capa extraídas via CNNs, para treinar regressões ou modelos de boosting capazes de prever valor aproximado de um item.

4.2 Sistemas de Recomendação

Com os dados de categoria, título e metadados, o sistema suporta recomendações usando:
- similaridade textual entre títulos (cosine similarity),
- embeddings NLP gerados por BERT, Sentence-BERT ou Word2Vec,
- categorias correlacionadas,
- métodos colaborativos como LightFM ou matrix factorization.

Isso permite construir um “Sommelier de Livros”, sugerindo ao usuário obras que combinam com seu gosto.

4.3 Análise de Mercado

A camada de insights expõe informações prontas para:
- comparar preços por categoria,
- entender a distribuição de avaliações,
- identificar livros premium vs populares,
- acompanhar variações temporalizadas do catálogo (futuro).

Esses dados podem alimentar dashboards ou análises exploratórias.

4.4 API de Feature Store

A arquitetura prevê a criação de endpoints futuros como:
/api/v2/features/book/<id>

Essa API entregaria vetores de características pré-calculadas (ex.: embedding do título, categoria one-hot, preço normalizado).
Tais vetores podem ser diretamente consumidos por modelos de ML, economizando tempo e padronizando o fluxo.

## 5. 🤖 Plano de Integração com Modelos de ML
A arquitetura prevê quatro estágios de maturidade para integração de machine learning:

5.1 Estágio 1 — Preparação dos Dados

Criar um diretório /ml e consolidar datasets com:
Pythonimport pandas as pddf = pd.read_csv("data/books.csv")Mostrar mais linhas
Aqui acontecem:
- limpeza adicional,
- geração de features,
- splits de treino/validação.


5.2 Estágio 2 — Treinamento

Modelos recomendados:
- RandomForest — fácil de treinar, ótimo baseline para regressão.
- XGBoost/LightGBM — alta performance para ranking e regressão.
- BERT/Sentence-BERT — representações semânticas para títulos.
- LightFM — recomendação colaborativa.


5.3 Estágio 3 — Deploy de Modelos na API

A API pode ganhar endpoints como:
POST /api/v2/predictions/price
POST /api/v2/recommendations

Nesses endpoints, o modelo carregado em memória recebe features e devolve a inferência.

5.4 Estágio 4 — MLOps

Para produção, o ciclo completo incluiria:
- monitoramento de drift,
- versionamento de modelos,
- benchmark automático,
- reprocessamento de dados,
- Feature Store compartilhada.

## 6. 📦 Componentes Críticos do Sistema
O BookScraper é responsável pela coleta de páginas e extração dos campos brutos. O CSVWriter atua como camada de persistência intermediária, gravando os dados em CSV. O BookImportService realiza a leitura do arquivo, normaliza dados e evita duplicidades antes de inserir no banco. O BookRepository fornece abstrações de acesso ao banco via SQLAlchemy, enquanto o Modelo Book representa a entidade persistida. O Books Blueprint expõe a API pública principal e o Insights Blueprint concentra endpoints analíticos em Pandas. O Dockerfile empacota a aplicação como container, e o docker-compose orquestra o ambiente com API e Postgres. Por fim, o Alembic controla a evolução do schema do banco.

## 7. 📚 Tecnologias e Decisões Arquiteturais
A solução utiliza Python, Flask com Blueprints, SQLAlchemy com PostgreSQL, Requests e BeautifulSoup para scraping, Pandas para análises, Docker e docker-compose para infraestrutura e Alembic para migrações. O CSV funciona como fonte intermediária simples e eficiente.

## 8. 🧾 Conclusão
A arquitetura do Book Sommelier API é modular, extensível e preparada para o futuro. Ela separa claramente scraping, processamento, API e análise, servindo tanto aplicações quanto cientistas de dados. O design facilita escalabilidade, adição de novos scrapers, criação de novas features e integração com pipelines de machine learning e MLOps.



