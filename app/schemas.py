from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PublicacaoRead(BaseModel):
    id: int
    concurso_id: int
    titulo: str
    data_publicacao: Optional[str] = None
    url_arquivo: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConcursoRead(BaseModel):
    id: int
    tipo_id: int
    tipo_descricao: str
    numero: Optional[int] = None
    ano: Optional[int] = None
    titulo: str
    situacao_id: Optional[int] = None
    situacao_descricao: Optional[str] = None
    unidade: Optional[str] = None
    link_pagina: Optional[str] = None
    destaque: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConcursoDetail(ConcursoRead):
    detalhes_html: Optional[str] = None
    publicacoes: List[PublicacaoRead] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedConcursos(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: List[ConcursoRead]


class SyncResult(BaseModel):
    synced_concursos: int
    synced_publicacoes: int
    status: str
