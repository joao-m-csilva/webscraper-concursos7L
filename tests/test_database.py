import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, Concurso, Publicacao
from app.service import get_concurso, list_concursos, sync_concursos, upsert_concurso


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_upsert_concurso_create_and_update(db_session: Session):
    row = {
        "CDPROCSELETIVO": 1,
        "CDTIPO": 1,
        "NMTIPO": "Concurso Público",
        "NUPROCSELETIVO": 10,
        "NUANOPROCSELETIVO": 2026,
        "NMTITULO": "Concurso Guarda Municipal",
        "CDSITUACAO": 1,
        "NMSITUACAO": "Inscrições abertas",
        "NMUNIDADE": "Segurança",
        "DSINFORMACOES": "<p>Edital aberto</p>",
        "STDESTAQUE": True
    }
    pubs = [
        {"titulo": "Edital Retificado", "data_publicacao": "01/01/2026", "url_arquivo": "https://test.com/edital.pdf"}
    ]

    concurso, new_pubs = upsert_concurso(db_session, row, pubs, "https://test.com")
    db_session.commit()

    assert concurso.id == 1
    assert concurso.titulo == "Concurso Guarda Municipal"
    assert new_pubs == 1

    # Test update and idempotency of existing publications
    row["NMTITULO"] = "Concurso Guarda Municipal - Retificado"
    updated_concurso, updated_pubs = upsert_concurso(db_session, row, pubs, "https://test.com")
    db_session.commit()

    assert updated_concurso.titulo == "Concurso Guarda Municipal - Retificado"
    assert updated_pubs == 0


def test_list_concursos_filters(db_session: Session):
    c1 = Concurso(
        id=1,
        tipo_id=1,
        tipo_descricao="Concurso Público",
        numero=1,
        ano=2026,
        titulo="Concurso Educacao",
        situacao_id=1,
        situacao_descricao="Inscrições abertas",
        unidade="SME",
        destaque=False
    )
    c2 = Concurso(
        id=2,
        tipo_id=2,
        tipo_descricao="Processo Seletivo Simplificado",
        numero=2,
        ano=2025,
        titulo="Processo Saude",
        situacao_id=3,
        situacao_descricao="Encerrado",
        unidade="SMS",
        destaque=False
    )
    db_session.add_all([c1, c2])
    db_session.commit()

    # Filter by ano
    items, total, _ = list_concursos(db_session, ano=2026)
    assert total == 1
    assert items[0].id == 1

    # Filter by apenas_concursos
    items, total, _ = list_concursos(db_session, apenas_concursos=True)
    assert total == 1
    assert items[0].id == 1

    # Filter by situacao
    items, total, _ = list_concursos(db_session, situacao="Encerrado")
    assert total == 1
    assert items[0].id == 2

    # Filter by text search query
    items, total, _ = list_concursos(db_session, query="Saude")
    assert total == 1
    assert items[0].id == 2


def test_get_concurso(db_session: Session):
    c = Concurso(
        id=99,
        tipo_id=1,
        tipo_descricao="Concurso",
        titulo="Concurso Teste",
        destaque=False
    )
    db_session.add(c)
    db_session.commit()

    found = get_concurso(db_session, 99)
    assert found is not None
    assert found.titulo == "Concurso Teste"

    not_found = get_concurso(db_session, 999)
    assert not_found is None


def test_sync_concursos_service(db_session: Session):
    class MockScraper:
        base_url = "https://www.setelagoas.mg.gov.br"

        def fetch_processos(self, page, size, cd_tipo):
            if page == 0:
                return [{
                    "CDPROCSELETIVO": 55,
                    "CDTIPO": 1,
                    "NMTIPO": "Concurso Público",
                    "NUPROCSELETIVO": 3,
                    "NUANOPROCSELETIVO": 2026,
                    "NMTITULO": "Concurso Teste Sync",
                    "CDSITUACAO": 1,
                    "NMSITUACAO": "Aberto",
                    "NMUNIDADE": "Educacao",
                    "DSINFORMACOES": "Desc",
                    "STDESTAQUE": False
                }]
            return []

        def fetch_publicacoes(self, cd_proc_seletivo):
            return [{"titulo": "Edital Sync", "data_publicacao": "01/01/2026", "url_arquivo": "https://file.pdf"}]

    c_count, p_count = sync_concursos(db_session, MockScraper(), pages=1, page_size=10, fetch_details=True)
    assert c_count == 1
    assert p_count == 1

