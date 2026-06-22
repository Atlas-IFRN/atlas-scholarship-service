# Scholarship Service 🎓

Serviço de gerenciamento de bolsas de estudo desenvolvido com Django 5.x e Docker.

---

## 🛠️ Setup Local (Com Docker) - Recomendado

A forma mais rápida de rodar o projeto é utilizando o Docker, pois ele já configura todo o ambiente para você.

1.  **Clone o repositório:**
    No terminal:
    git clone <url-do-repositorio>
    cd scholarship-service

2.  **Configure as variáveis de ambiente:**
    Crie um arquivo chamado `.env` na raiz do projeto e cole as informações que estão presentes no .env.example

3. **Crie um ambiente virtual e o ative**
    python -m venv .venv

    No windows: .\.venv\Scripts\activate
    No linux: source .venv/bin/activate

4. **Baixe as dependências presentes no requirements.txt**
    pip install django django-environ
    ou
    pip install -r requirements.txt

5.  **Suba o container:**
    docker compose up --build

6.  **Rode as migrações iniciais:**
    Em um novo terminal, execute:
    docker compose exec scholarship python manage.py makemigrations
    docker compose exec scholarship python manage.py migrate

7.  **Acesse o serviço:**
    O projeto estará disponível em: http://localhost:8000

---

## 🧪 Comandos Úteis

* **Criar Superusuário (Admin):**
    `docker-compose exec web python manage.py createsuperuser`
* **Criar Migrações:**
    `docker-compose exec web python manage.py makemigrations`
* **Parar Containers:**
    `docker-compose down`

---
### Documentação Swagger da API
A documentação interativa da API é gerada automaticamente pelo `drf-spectacular` e `OpenAPI 3.0`.

## Para acessá-la localmente, suba o container docker e acesse a seguinte URL em seu navegador:
http://127.0.0.1:8000/swagger/

## Exemplos de payloads

Todos os endpoints abaixo exigem o header `Authorization: Bearer <token>`.

### Criar uma tecnologia

`POST /api/scholarship/technologies/`

```json
{
  "name": "Python"
}
```

### Criar uma bolsa estudantil

`POST /api/scholarship/scholarships/`

Os campos `id`, `published_by`, `user_application`, `created_at` e `updated_at`
são preenchidos pela API e não devem ser enviados.

```json
{
  "title": "Sistema de Monitoramento com IoT e Machine Learning",
  "description": "Pesquisa aplicada a soluções embarcadas com coleta de dados em tempo real.",
  "value_per_month": "750.00",
  "duration_in_months": 12,
  "vacancies": 4,
  "minimum_period": 3,
  "minimum_ira": "7.00",
  "status": "Open",
  "phases": [
    {
      "title": "Inscrições",
      "start_date": "2026-06-14T23:54:38-03:00",
      "end_date": "2026-06-30T23:54:45-03:00",
      "type": "Registration",
      "display_order": 1
    },
    {
      "title": "Seleção",
      "start_date": "2026-07-01T08:00:00-03:00",
      "end_date": "2026-07-05T18:00:00-03:00",
      "type": "Selection",
      "display_order": 2
    }
  ],
  "links": [
    {
      "label": "Edital",
      "url": "https://suap.ifrn.edu.br/",
      "display_order": 1
    }
  ],
  "requirements": [
    {
      "title": "Conhecimento em Python",
      "description": "Ter concluído a trilha de backend com Python.",
      "display_order": 1
    }
  ],
  "technologies": [
    "98e4789a-b16b-4a8c-9376-e41a8f8e9ca3"
  ]
}
```

Os status aceitos são `Draft`, `Open`, `RegistrationClosed` e `Closed`. Os tipos
de fase aceitos são `Registration`, `Selection`, `Result` e `Other`.

### Atualizar parcialmente uma bolsa

`PATCH /api/scholarship/scholarships/<uuid-da-bolsa>/`

```json
{
  "status": "RegistrationClosed",
  "vacancies": 3
}
```

### Trecho da resposta do detalhe de uma bolsa para estudante

`GET /api/scholarship/scholarships/<uuid-da-bolsa>/`

O campo `user_application` informa se o estudante autenticado já possui uma
candidatura. Para professores, esse campo retorna `null`.

```json
{
  "id": "c740cd62-e16f-40a7-aa40-8c61c91519c9",
  "title": "Sistema de Monitoramento com IoT e Machine Learning",
  "status": "Open",
  "user_application": {
    "applied": true,
    "application_id": "7ee3cf8a-30cb-4e62-82eb-5ca41781a581",
    "status": "Enrolled"
  }
}
```

### Criar uma candidatura

`POST /api/scholarship/scholarships/<uuid-da-bolsa>/apply/`

O corpo pode ser vazio. A bolsa é obtida pela URL e os dados do estudante são
obtidos do token validado pelo serviço de autenticação.

```json
{}
```

### Atualizar o status de uma candidatura

`PATCH /api/scholarship/applications/<uuid-da-candidatura>/`

```json
{
  "status": "Approved"
}
```

Os status aceitos são `Cancelled`, `Enrolled`, `Approved` e `Rejected`.

### Cancelar a própria candidatura

`PATCH /api/scholarship/scholarships/<uuid-da-bolsa>/cancel/`

```json
{}
```

### Resposta paginada de uma listagem

```json
{
  "count": 24,
  "next": "http://localhost:8002/api/scholarship/scholarships/?page=2",
  "previous": null,
  "results": []
}
```

### Criar um registro no banco de talentos

```json
{
  "student_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "is_actively_looking": true
}
```

### Criar uma entrevista

```json
{
  "interviewer_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "description": "O aluno se comunica bem e possui conhecimento técnico.",
  "interview_date": "2026-05-15T21:23:43.538000-03:00",
  "talent_registration": "UUID-DO-REGISTRO-NO-BANCO-DE-TALENTOS-AQUI",
  "application": "UUID-DA-INSCRIÇÃO-AQUI (OPCIONAL)"
}
```


### Como atualizar a documentação
A documentação reflete o código atual. Sempre que adicionar uma nova rota, atualizar um `Serializer` ou alterar as permissões de uma View, o Swagger será atualizado automaticamente.
