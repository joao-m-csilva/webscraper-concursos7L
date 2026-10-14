import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.database import get_db
from app.main import app
from app.models import Base, Concurso, Publicacao


@pytest.fixture
def client_with_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Populate seed data for API testing
    db = TestingSessionLocal()
    concurso = Concurso(
        id=10,
        tipo_id=1,
        tipo_descricao="Concurso Público",
        numero=5,
        ano=2026,
        titulo="Concurso Especial",
        situacao_id=1,
        situacao_descricao="Inscrições abertas",
        unidade="Prefeitura",
        destaque=False
    )
    pub = Publicacao(
        id=1,
        concurso_id=10,
        titulo="Edital 05/2026",
        data_publicacao="01/02/2026",
        url_arquivo="https://test.com/edital.pdf"
    )
    db.add(concurso)
    db.add(pub)
    db.commit()
    db.close()

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_root_endpoint(client_with_db: TestClient):
    response = client_with_db.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs_url"] == "/docs"


def test_health_endpoint(client_with_db: TestClient):
    response = client_with_db.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_concursos_list(client_with_db: TestClient):
    response = client_with_db.get("/concursos?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == 10
    assert data["items"][0]["titulo"] == "Concurso Especial"


def test_get_concursos_filter_empty(client_with_db: TestClient):
    response = client_with_db.get("/concursos?ano=1999")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_concurso_detail_found(client_with_db: TestClient):
    response = client_with_db.get("/concursos/10")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["titulo"] == "Concurso Especial"
    assert len(data["publicacoes"]) == 1
    assert data["publicacoes"][0]["titulo"] == "Edital 05/2026"


def test_get_concurso_detail_not_found(client_with_db: TestClient):
    response = client_with_db.get("/concursos/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_trigger_sync_mock(client_with_db: TestClient, monkeypatch):
    from app import main

    class DummyScraper:
        def fetch_processos(self, page, size, cd_tipo):
            return [{
                "CDPROCSELETIVO": 20,
                "CDTIPO": 1,
                "NMTIPO": "Concurso Público",
                "NUPROCSELETIVO": 1,
                "NUANOPROCSELETIVO": 2026,
                "NMTITULO": "Concurso Mock",
                "CDSITUACAO": 2,
                "NMSITUACAO": "Em andamento",
                "NMUNIDADE": "Admin",
                "DSINFORMACOES": "Desc",
                "STDESTAQUE": False
            }]

        def fetch_publicacoes(self, cd_proc_seletivo):
            return [{"titulo": "Edital Mock", "data_publicacao": "02/02/2026", "url_arquivo": "https://url.com"}]

        base_url = "https://www.setelagoas.mg.gov.br"

    monkeypatch.setattr(main, "PrefeituraSeteLagoasScraper", DummyScraper)

    response = client_with_db.post("/concursos/sync?pages=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["synced_concursos"] == 1
    assert data["synced_publicacoes"] == 1
    assert data["status"] == "success"
