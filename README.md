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

4. **Baixe o django e django-environ ou as dependências presentes no requirements.txt**
    pip install django django-environ
    ou
    pip install -r requirements.txt

5.  **Suba o container:**
    docker-compose up --build

6.  **Rode as migrações iniciais:**
    Em um novo terminal, execute:
    docker-compose exec scholarship python manage.py migrate

7.  **Acesse o serviço:**
    O projeto estará disponível em: http://localhost:8000

---

## 📂 Estrutura de Pastas

* `apps/`: Contém os aplicativos de negócio (ex: `scholarship`).
* `config/`: Configurações do Django divididas por ambiente (`base.py`, `local.py`).
* `.env`: Arquivo local para variáveis sensíveis (não versionado).
* `requirements.txt`: Lista de dependências do Python.

---

## 🧪 Comandos Úteis

* **Criar Superusuário (Admin):**
    `docker-compose exec scholarship python manage.py createsuperuser`
* **Criar Migrações:**
    `docker-compose exec scholarship python manage.py makemigrations`
* **Parar Containers:**
    `docker-compose down`
