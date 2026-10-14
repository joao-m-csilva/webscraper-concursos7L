from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.schemas import ConcursoDetail, PaginatedConcursos
from app.service import get_concurso, list_concursos


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

