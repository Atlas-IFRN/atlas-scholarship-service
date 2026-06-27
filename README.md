# Scholarship Service 🎓

Microserviço do ecossistema **Atlas** responsável pelo gerenciamento de bolsas de estudo, candidaturas, banco de talentos e pontuação de alunos.

## Stack

- Python · Django 5.x · Django REST Framework
- PostgreSQL · Redis · RabbitMQ + Celery
- Docker · drf-spectacular (Swagger/OpenAPI 3.0)

## Executando localmente

Este serviço é orquestrado junto com todos os outros pelo repositório central de infraestrutura:

> **[Atlas-IFRN/atlas-infra](https://github.com/Atlas-IFRN/atlas-infra)** — Docker Compose canônico, Nginx, scripts de deploy e backup.

Para subir apenas a infraestrutura compartilhada (Postgres, Redis, RabbitMQ) e rodar este serviço isolado em modo dev:

```bash
# 1. Suba a infra compartilhada
git clone https://github.com/Atlas-IFRN/atlas-infra
cd atlas-infra
docker compose -f docker-compose.dev.yml up -d

# 2. Neste repositório
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

## Variáveis de ambiente

Crie um `.env` baseado no `.env.example`. Principais: `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `AUTH_SERVICE_URL`, `INTERNAL_TOKEN`.

## Documentação da API

Com o serviço rodando, acesse a documentação interativa:

- **Swagger UI:** `http://localhost:8002/swagger/`

## Exemplos de payload

**Criar tecnologia:**
```json
{"name": "Python"}
```

**Criar bolsa:**
```json
{
  "title": "Monitoria de Algoritmos 2026.1",
  "description": "Auxílio a alunos do primeiro ano nas disciplinas de programação.",
  "value_per_month": 700.00,
  "duration_in_months": 6,
  "vacancies": 4,
  "minimum_period": 2,
  "minimum_ira": 7.5,
  "orientator_id": "84825945-8370-496e-9080-692797e556e4",
  "registration_start": "2026-05-13T20:51:53Z",
  "registration_end": "2026-10-13T20:51:53Z",
  "technologies": ["UUID-DA-TECNOLOGIA"],
  "phases": [{"title": "Entrevistas", "start_date": "2026-06-01T08:00:00Z", "end_date": "2026-06-15T23:59:59Z", "display_order": 1}],
  "links": [{"label": "Edital Oficial", "url": "https://universidade.edu/edital.pdf", "type": "Edital", "display_order": 1}],
  "requirements": [{"title": "Nota em Algoritmos I", "description": "Média >= 8.0", "display_order": 1}]
}
```

**Candidatar-se a uma bolsa:**
```json
{"scholarship": "UUID-DA-BOLSA"}
```

**Entrar no banco de talentos:**
```json
{"is_actively_looking": true}
```

## Comandos úteis

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py test
```

