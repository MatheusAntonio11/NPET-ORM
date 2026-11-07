from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Usuario


class UsuarioRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_all(self, skip: int = 0, limit: int = 50) -> Sequence[Usuario]:
        stmt = select(Usuario).order_by(Usuario.id_usuario).offset(skip).limit(limit)
        return self._db.scalars(stmt).all()

    def get_by_id(self, id_usuario: int) -> Usuario | None:
        return self._db.get(Usuario, id_usuario)

    def email_exists(self, email: str) -> bool:
        stmt = select(Usuario.id_usuario).where(Usuario.email == email)
        return self._db.scalar(stmt) is not None

    def cpf_exists(self, cpf: str) -> bool:
        stmt = select(Usuario.id_usuario).where(Usuario.cpf == cpf)
        return self._db.scalar(stmt) is not None

    def update(self, usuario: Usuario) -> Usuario:
        self._db.commit()
        self._db.refresh(usuario)
        return usuario

    def delete(self, usuario: Usuario) -> None:
        self._db.delete(usuario)
        self._db.commit()