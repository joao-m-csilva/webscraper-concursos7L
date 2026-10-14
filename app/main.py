from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.schemas import ConcursoDetail, PaginatedConcursos, SyncResult
from app.scraper import PrefeituraSeteLagoasScraper
from app.service import get_concurso, list_concursos, sync_concursos


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Prefeitura de Sete Lagoas - Concursos & Processos Seletivos API",
    description="API RESTful para consulta e monitoramento de concursos e processos seletivos públicos da Prefeitura de Sete Lagoas (MG).",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Info"])
def root():
    return {
        "message": "Prefeitura de Sete Lagoas Concursos API",
        "docs_url": "/docs",
        "endpoints": {
            "concursos": "/concursos",
            "health": "/health"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.get("/concursos", response_model=PaginatedConcursos, tags=["Concursos"])
def get_concursos(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    tipo: Optional[str] = Query(None, description="Filter by type name (e.g. 'Concurso', 'Processo Seletivo')"),
    tipo_id: Optional[int] = Query(None, description="Filter by type ID (1: Concurso Público, 2: Simplificado, etc.)"),
    situacao: Optional[str] = Query(None, description="Filter by status (e.g. 'Inscrições abertas', 'Homologado')"),
    situacao_id: Optional[int] = Query(None, description="Filter by status ID"),
    ano: Optional[int] = Query(None, description="Filter by year"),
    q: Optional[str] = Query(None, description="Search keyword in title or department"),
    apenas_concursos: bool = Query(False, description="Restrict to Concursos Públicos (tipo_id=1)"),
    db: Session = Depends(get_db)
):
    items, total, pages = list_concursos(
        db=db,
        page=page,
        size=size,
        tipo=tipo,
        tipo_id=tipo_id,
        situacao=situacao,
        situacao_id=situacao_id,
        ano=ano,
        query=q,
        apenas_concursos=apenas_concursos
    )
    return PaginatedConcursos(
        total=total,
        page=page,
        size=size,
        pages=pages,
        items=items
    )


@app.get("/concursos/{concurso_id}", response_model=ConcursoDetail, tags=["Concursos"])
def get_concurso_detail(concurso_id: int, db: Session = Depends(get_db)):
    concurso = get_concurso(db, concurso_id)
    if not concurso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concurso with ID {concurso_id} not found"
        )
    return concurso


@app.post("/concursos/sync", response_model=SyncResult, tags=["Scraper"])
def trigger_sync(
    pages: int = Query(1, ge=1, le=10, description="Number of pages to scrape"),
    page_size: int = Query(20, ge=1, le=50, description="Items per page from portal"),
    tipo_id: Optional[int] = Query(None, description="Filter by specific type ID"),
    fetch_details: bool = Query(True, description="Fetch publications and attached PDF links"),
    db: Session = Depends(get_db)
):
    scraper = PrefeituraSeteLagoasScraper()
    synced_c, synced_p = sync_concursos(
        db=db,
        scraper=scraper,
        pages=pages,
        page_size=page_size,
        cd_tipo=tipo_id,
        fetch_details=fetch_details
    )
    return SyncResult(
        synced_concursos=synced_c,
        synced_publicacoes=synced_p,
        status="success"
    )
