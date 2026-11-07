from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.database.models import Instituicao


class InstituicaoRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Instituicao]:
        stmt = (
            select(Instituicao)
            .order_by(Instituicao.id_instituicao)
            .offset(skip)
            .limit(limit)
        )
        return self._db.scalars(stmt).all()

    def get_by_id(self, id_instituicao: int) -> Instituicao | None:
        return self._db.get(Instituicao, id_instituicao)

    def get_by_user_id(self, id_usuario: int) -> Instituicao | None:
        stmt = select(Instituicao).where(Instituicao.id_usuario == id_usuario)
        return self._db.scalar(stmt)

    def cnpj_exists(self, cnpj: str) -> bool:
        stmt = select(Instituicao.id_instituicao).where(Instituicao.cnpj == cnpj)
        return self._db.scalar(stmt) is not None

    def create(self, instituicao: Instituicao) -> Instituicao:
        self._db.add(instituicao)
        self._db.commit()
        self._db.refresh(instituicao)
        return instituicao

    def update(self, instituicao: Instituicao) -> Instituicao:
        self._db.commit()
        self._db.refresh(instituicao)
        return instituicao

    def delete(self, instituicao: Instituicao) -> None:
        try:
            self._db.delete(instituicao)
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            raise ConflictError(
                "Não é possível excluir: a instituição possui registros vinculados (ex.: doações)."
            )