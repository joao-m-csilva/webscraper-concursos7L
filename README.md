# Sete Lagoas Concursos Scraper & API

> **Language / Idioma:** [English (EN-US)](#english-en-us) | [Português (PT-BR)](#português-pt-br)

---

## Português (PT-BR)

Web scraper e API RESTful para monitoramento e consulta de concursos públicos e processos seletivos da Prefeitura Municipal de Sete Lagoas (MG).

### Arquitetura

* **Linguagem:** Python 3.11+
* **API Framework:** FastAPI + Uvicorn
* **Scraper:** HTTPX + BeautifulSoup4 (comunicação direta com o backend AjaxPro/DataTable)
* **Banco de Dados & ORM:** SQLite (desenvolvimento/testes) e PostgreSQL (produção) via SQLAlchemy 2.0
* **Testes Automatizados:** Pytest (23 testes unitários e de integração)

### Estrutura do Projeto

```text
├── app/
│   ├── config.py       # Configurações de ambiente (Pydantic Settings)
│   ├── database.py     # Inicialização e sessões do SQLAlchemy
│   ├── models.py       # Modelos Concurso e Publicacao
│   ├── schemas.py      # Schemas Pydantic para serialização da API
│   ├── scraper.py      # Parser e cliente HTTP para a Prefeitura de Sete Lagoas
│   ├── service.py      # Lógica de sincronização e consultas
│   └── main.py         # Aplicação FastAPI e rotas REST
├── tests/              # Suíte de testes unitários e de integração
├── run_scraper.py      # CLI runner independente para agendamento/cron
├── Dockerfile          # Container da API
├── docker-compose.yml  # Configuração com PostgreSQL e API
└── requirements.txt    # Dependências do projeto
```

### Instalação e Execução Local

#### 1. Criar e Ativar Ambiente Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Executar Testes Automatizados
```bash
pytest -v
```

#### 3. Executar o Scraper via CLI
```bash
python run_scraper.py --pages 2
```

#### 4. Iniciar a API
```bash
uvicorn app.main:app --reload --port 8000
```
Documentação interativa Swagger disponível em: `http://localhost:8000/docs`

### Endpoints da API

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| `GET` | `/health` | Status de saúde da aplicação |
| `GET` | `/concursos` | Listagem paginada com filtros (`page`, `size`, `ano`, `situacao`, `tipo`, `q`, `apenas_concursos`) |
| `GET` | `/concursos/{id}` | Detalhes do concurso e lista de publicações/PDFs anexos |
| `POST` | `/concursos/sync` | Gatilho manual para execução do scraper |

### Execução com Docker Compose

```bash
docker compose up --build -d
```
A API estará acessível em `http://localhost:8000`.

---

## English (EN-US)

Web scraper and RESTful API designed to monitor and query public tenders, civil service exams, and selection processes published by the City Hall of Sete Lagoas (Minas Gerais, Brazil).

### Architecture

* **Language:** Python 3.11+
* **API Framework:** FastAPI + Uvicorn
* **Scraper Engine:** HTTPX + BeautifulSoup4 (direct communication with the underlying AjaxPro/DataTable endpoints)
* **Database & ORM:** SQLite (local development/tests) and PostgreSQL (production) via SQLAlchemy 2.0
* **Automated Testing:** Pytest (23 unit and integration tests)

### Project Layout

```text
├── app/
│   ├── config.py       # Environment configuration (Pydantic Settings)
│   ├── database.py     # SQLAlchemy engine and session factory
│   ├── models.py       # Concurso and Publicacao database models
│   ├── schemas.py      # Pydantic schemas for request/response serialization
│   ├── scraper.py      # Sete Lagoas City Hall parser and HTTP client
│   ├── service.py      # Synchronization and query service layer
│   └── main.py         # FastAPI instance and REST routes
├── tests/              # Comprehensive unit and integration test suite
├── run_scraper.py      # Standalone CLI runner for automated cron jobs
├── Dockerfile          # Production containerfile for the API
├── docker-compose.yml  # Multi-container setup with PostgreSQL and API
└── requirements.txt    # Application dependencies
```

### Local Setup & Execution

#### 1. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Run Test Suite
```bash
pytest -v
```

#### 3. Run Scraper via CLI
```bash
python run_scraper.py --pages 2
```

#### 4. Start API Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger UI documentation is available at: `http://localhost:8000/docs`

### API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check probe |
| `GET` | `/concursos` | Paginated listing with filtering (`page`, `size`, `ano`, `situacao`, `tipo`, `q`, `apenas_concursos`) |
| `GET` | `/concursos/{id}` | Contest details including attached publications and PDF notices |
| `POST` | `/concursos/sync` | Manual trigger endpoint to trigger crawler execution |

### Running with Docker Compose

```bash
docker compose up --build -d
```
The API will be available at `http://localhost:8000`.
