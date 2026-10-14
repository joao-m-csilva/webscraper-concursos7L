# Sete Lagoas Concursos Scraper & API

> **Language / Idioma:** [English (EN-US)](#english-en-us) | [Português (PT-BR)](#português-pt-br)

[![API Status](https://img.shields.io/badge/status-online-brightgreen)](https://webscraper-concursos7l.onrender.com/health)
[![API Docs](https://img.shields.io/badge/docs-Swagger%20UI-blue)](https://webscraper-concursos7l.onrender.com/docs)
[![Database](https://img.shields.io/badge/database-Supabase%20PostgreSQL-3ECF8E)](https://supabase.com)
[![Automation](https://img.shields.io/badge/automation-GitHub%20Actions-2088FF)](https://github.com/joao-m-csilva/webscraper-concursos7L/actions)

---

## Português (PT-BR)

Web scraper e API RESTful para monitoramento e consulta de concursos públicos e processos seletivos da Prefeitura Municipal de Sete Lagoas (MG).

### Acesso em Produção

* **URL Base da API:** [https://webscraper-concursos7l.onrender.com](https://webscraper-concursos7l.onrender.com)
* **Documentação Interativa (Swagger UI):** [https://webscraper-concursos7l.onrender.com/docs](https://webscraper-concursos7l.onrender.com/docs)
* **Health Check:** [https://webscraper-concursos7l.onrender.com/health](https://webscraper-concursos7l.onrender.com/health)

### Arquitetura e Infraestrutura

* **API Framework:** FastAPI + Uvicorn
* **Linguagem:** Python 3.11+
* **Hospedagem da API:** [Render](https://render.com) (Container Docker)
* **Banco de Dados:** [Supabase](https://supabase.com) (PostgreSQL gerenciado) via SQLAlchemy 2.0
* **Agendamento do Scraper:** [GitHub Actions](https://github.com/joao-m-csilva/webscraper-concursos7L/actions) (rotina automática executada a cada 12 horas)
* **Scraper Engine:** HTTPX + BeautifulSoup4 (comunicação direta com o backend AjaxPro/DataTable)
* **Testes Automatizados:** Pytest (23 testes unitários e de integração)

### Estrutura do Projeto

```text
├── .github/workflows/
│   └── scraper.yml     # Workflow agendado do GitHub Actions (cron 12h)
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

### Endpoints da API

| Método | Rota | Descrição | Exemplo de Parâmetros |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Status de saúde da aplicação | - |
| `GET` | `/concursos` | Listagem paginada com filtros | `?apenas_concursos=true&ano=2026&page=1&size=10` |
| `GET` | `/concursos/{id}` | Detalhes do concurso e lista de publicações/PDFs | `/concursos/23344` |
| `POST` | `/concursos/sync` | Gatilho manual para execução do scraper | `?pages=2&page_size=20` |

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

#### 4. Iniciar a API Localmente
```bash
uvicorn app.main:app --reload --port 8000
```

---

## English (EN-US)

Web scraper and RESTful API designed to monitor and query public tenders, civil service exams, and selection processes published by the City Hall of Sete Lagoas (Minas Gerais, Brazil).

### Live Production Access

* **API Base URL:** [https://webscraper-concursos7l.onrender.com](https://webscraper-concursos7l.onrender.com)
* **Interactive Documentation (Swagger UI):** [https://webscraper-concursos7l.onrender.com/docs](https://webscraper-concursos7l.onrender.com/docs)
* **Health Check:** [https://webscraper-concursos7l.onrender.com/health](https://webscraper-concursos7l.onrender.com/health)

### Architecture & Infrastructure

* **API Framework:** FastAPI + Uvicorn
* **Language:** Python 3.11+
* **API Hosting:** [Render](https://render.com) (Docker Container)
* **Database:** [Supabase](https://supabase.com) (Managed PostgreSQL) via SQLAlchemy 2.0
* **Scraper Scheduling:** [GitHub Actions](https://github.com/joao-m-csilva/webscraper-concursos7L/actions) (automated cron job executing every 12 hours)
* **Scraper Engine:** HTTPX + BeautifulSoup4 (direct communication with the underlying AjaxPro/DataTable endpoints)
* **Automated Testing:** Pytest (23 unit and integration tests)

### Project Layout

```text
├── .github/workflows/
│   └── scraper.yml     # GitHub Actions cron workflow (runs every 12h)
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

### API Endpoints

| Method | Endpoint | Description | Sample Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health check probe | - |
| `GET` | `/concursos` | Paginated listing with filtering | `?apenas_concursos=true&ano=2026&page=1&size=10` |
| `GET` | `/concursos/{id}` | Contest details including attached publications and PDF notices | `/concursos/23344` |
| `POST` | `/concursos/sync` | Manual trigger endpoint to trigger crawler execution | `?pages=2&page_size=20` |

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

#### 4. Start API Server Locally
```bash
uvicorn app.main:app --reload --port 8000
```
