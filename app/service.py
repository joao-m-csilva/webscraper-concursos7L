import math
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Concurso, Publicacao
from app.scraper import PrefeituraSeteLagoasScraper


def upsert_concurso(db: Session, row: Dict[str, Any], publicacoes_data: List[Dict[str, Any]], base_url: str) -> Tuple[Concurso, int]:
    cd_proc = int(row["CDPROCSELETIVO"])
    concurso = db.get(Concurso, cd_proc)

    link_page = f"{base_url}/proc_sel_vis.aspx?cd={cd_proc}"

    if not concurso:
        concurso = Concurso(
            id=cd_proc,
            tipo_id=int(row.get("CDTIPO", 0)),
            tipo_descricao=str(row.get("NMTIPO", "")),
            numero=int(row["NUPROCSELETIVO"]) if row.get("NUPROCSELETIVO") is not None else None,
            ano=int(row["NUANOPROCSELETIVO"]) if row.get("NUANOPROCSELETIVO") is not None else None,
            titulo=str(row.get("NMTITULO", "")),
            situacao_id=int(row["CDSITUACAO"]) if row.get("CDSITUACAO") is not None else None,
            situacao_descricao=str(row.get("NMSITUACAO", "")),
            unidade=str(row.get("NMUNIDADE", "")),
            detalhes_html=row.get("DSINFORMACOES"),
            link_pagina=link_page,
            destaque=bool(row.get("STDESTAQUE", False))
        )
        db.add(concurso)
    else:
        concurso.tipo_id = int(row.get("CDTIPO", concurso.tipo_id))
        concurso.tipo_descricao = str(row.get("NMTIPO", concurso.tipo_descricao))
        concurso.numero = int(row["NUPROCSELETIVO"]) if row.get("NUPROCSELETIVO") is not None else concurso.numero
        concurso.ano = int(row["NUANOPROCSELETIVO"]) if row.get("NUANOPROCSELETIVO") is not None else concurso.ano
        concurso.titulo = str(row.get("NMTITULO", concurso.titulo))
        concurso.situacao_id = int(row["CDSITUACAO"]) if row.get("CDSITUACAO") is not None else concurso.situacao_id
        concurso.situacao_descricao = str(row.get("NMSITUACAO", concurso.situacao_descricao))
        concurso.unidade = str(row.get("NMUNIDADE", concurso.unidade))
        concurso.detalhes_html = row.get("DSINFORMACOES", concurso.detalhes_html)
        concurso.link_pagina = link_page
        concurso.destaque = bool(row.get("STDESTAQUE", concurso.destaque))

    db.flush()

    # Reconcile publications for this concurso
    existing_pubs = db.execute(
        select(Publicacao).where(Publicacao.concurso_id == cd_proc)
    ).scalars().all()

    existing_map = {(p.titulo, p.url_arquivo): p for p in existing_pubs}
    new_count = 0

    for pub_info in publicacoes_data:
        key = (pub_info["titulo"], pub_info["url_arquivo"])
        if key not in existing_map:
            new_pub = Publicacao(
                concurso_id=cd_proc,
                titulo=pub_info["titulo"],
                data_publicacao=pub_info.get("data_publicacao"),
                url_arquivo=pub_info.get("url_arquivo")
            )
            db.add(new_pub)
            new_count += 1

    return concurso, new_count


def sync_concursos(
    db: Session,
    scraper: PrefeituraSeteLagoasScraper,
    pages: int = 1,
    page_size: int = 20,
    cd_tipo: Optional[int] = None,
    fetch_details: bool = True
) -> Tuple[int, int]:
    total_concursos = 0
    total_publicacoes = 0

    for p in range(pages):
        items = scraper.fetch_processos(page=p, size=page_size, cd_tipo=cd_tipo)
        if not items:
            break

        for row in items:
            cd_proc = int(row["CDPROCSELETIVO"])
            publicacoes_data: List[Dict[str, Any]] = []

            if fetch_details:
                try:
                    publicacoes_data = scraper.fetch_publicacoes(cd_proc)
                except Exception:
                    publicacoes_data = []

            _, new_pubs = upsert_concurso(db, row, publicacoes_data, scraper.base_url)
            total_concursos += 1
            total_publicacoes += new_pubs

    db.commit()
    return total_concursos, total_publicacoes


def list_concursos(
    db: Session,
    page: int = 1,
    size: int = 20,
    tipo: Optional[str] = None,
    tipo_id: Optional[int] = None,
    situacao: Optional[str] = None,
    situacao_id: Optional[int] = None,
    ano: Optional[int] = None,
    query: Optional[str] = None,
    apenas_concursos: bool = False
) -> Tuple[List[Concurso], int, int]:
    stmt = select(Concurso)

    if apenas_concursos:
        stmt = stmt.where(Concurso.tipo_id == 1)
    elif tipo_id is not None:
        stmt = stmt.where(Concurso.tipo_id == tipo_id)
    elif tipo:
        stmt = stmt.where(Concurso.tipo_descricao.ilike(f"%{tipo}%"))

    if situacao_id is not None:
        stmt = stmt.where(Concurso.situacao_id == situacao_id)
    elif situacao:
        stmt = stmt.where(Concurso.situacao_descricao.ilike(f"%{situacao}%"))

    if ano is not None:
        stmt = stmt.where(Concurso.ano == ano)

    if query:
        search_filter = or_(
            Concurso.titulo.ilike(f"%{query}%"),
            Concurso.unidade.ilike(f"%{query}%")
        )
        stmt = stmt.where(search_filter)

    total_query = select(Concurso.id).where(stmt.whereclause) if stmt.whereclause is not None else select(Concurso.id)
    total_records = len(db.execute(total_query).scalars().all())

    # Pagination calculation
    offset = (page - 1) * size
    total_pages = math.ceil(total_records / size) if total_records > 0 else 1

    stmt = stmt.order_by(Concurso.ano.desc(), Concurso.numero.desc(), Concurso.id.desc()).offset(offset).limit(size)
    items = db.execute(stmt).scalars().all()

    return list(items), total_records, total_pages


def get_concurso(db: Session, concurso_id: int) -> Optional[Concurso]:
    return db.get(Concurso, concurso_id)
