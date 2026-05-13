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
    `docker-compose exec scholarship python manage.py createsuperuser`
* **Criar Migrações:**
    `docker-compose exec scholarship python manage.py makemigrations`
* **Parar Containers:**
    `docker-compose down`

---
### Documentação Swagger da API
A documentação interativa da API é gerada automaticamente pelo `drf-spectacular` e `OpenAPI 3.0`.

## Para acessá-la localmente, suba o container docker e acesse a seguinte URL em seu navegador:
http://127.0.0.1:8000/swagger/

> **Nota:** Os exemplos de payloads para criação de Bolsas, Inscrições e Tecnologias estão embutidos diretamente na interface do Swagger.

### Como atualizar a documentação
A documentação reflete o código atual. Sempre que adicionar uma nova rota, atualizar um `Serializer` ou alterar as permissões de uma View, o Swagger será atualizado automaticamente. Use os decoradores `@extend_schema` nas Views para customizar descrições, tags e exemplos de payloads.
