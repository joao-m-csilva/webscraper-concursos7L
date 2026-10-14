from datetime import datetime, timezone
from typing import List
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Concurso(Base):
    __tablename__ = "concursos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    tipo_id: Mapped[int] = mapped_column(Integer, index=True)
    tipo_descricao: Mapped[str] = mapped_column(String(100), index=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=True)
    ano: Mapped[int] = mapped_column(Integer, index=True, nullable=True)
    titulo: Mapped[str] = mapped_column(String(500), index=True)
    situacao_id: Mapped[int] = mapped_column(Integer, index=True, nullable=True)
    situacao_descricao: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    unidade: Mapped[str] = mapped_column(String(255), nullable=True)
    detalhes_html: Mapped[str] = mapped_column(Text, nullable=True)
    link_pagina: Mapped[str] = mapped_column(String(500), nullable=True)
    destaque: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    publicacoes: Mapped[List["Publicacao"]] = relationship(
        "Publicacao",
        back_populates="concurso",
        cascade="all, delete-orphan",
        order_by="Publicacao.id.desc()"
    )


class Publicacao(Base):
    __tablename__ = "publicacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    concurso_id: Mapped[int] = mapped_column(Integer, ForeignKey("concursos.id", ondelete="CASCADE"), index=True)
    titulo: Mapped[str] = mapped_column(String(500))
    data_publicacao: Mapped[str] = mapped_column(String(50), nullable=True)
    url_arquivo: Mapped[str] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    concurso: Mapped["Concurso"] = relationship("Concurso", back_populates="publicacoes")
