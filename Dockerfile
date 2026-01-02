# Imagem base do Python 3.12
FROM python:3.12-slim

# Define variáveis de ambiente para evitar arquivos .pyc e buffer de log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala o Poetry
RUN pip install poetry

# Copia apenas os arquivos de configuração do Poetry primeiro (melhora o cache do Docker)
COPY pyproject.toml poetry.lock* ./

# Configura o Poetry para instalar as dependências no Python global do container
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copia o restante do código para o container
COPY . .

# Expõe a porta (o Flask por padrão usa 5000, mas você pode manter 8000 se preferir)
EXPOSE 8000

# Variável de ambiente para o Flask
ENV FLASK_APP=api/main.py

# Comando para rodar: Scraper -> Loader -> API
CMD ["sh", "-c", "python scripts/scraper.py && python scripts/loader.py && gunicorn --bind 0.0.0.0:8000 api.main:app"]