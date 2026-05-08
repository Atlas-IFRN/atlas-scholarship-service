# Usa a imagem oficial do Python 3.12 slim (mais leve)
FROM python:3.12-slim

# Variáveis de ambiente para otimizar o Python no Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema operacional necessárias para o PostgreSQL e compilações
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia os requisitos e instala as dependências Python
# (Certifique-se de ter rodado 'pip freeze > requirements.txt' antes)
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código do projeto para dentro da pasta /app no container
COPY . /app/

# Expõe a porta 8000
EXPOSE 8000

# Comando padrão para rodar a aplicação
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
