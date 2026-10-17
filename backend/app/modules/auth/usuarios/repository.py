from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Usuario


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_credential(self, email: str) -> Usuario | None:
        return self._db.scalar(select(Usuario).where(Usuario.email == email))

    def email_exists(self, email: str) -> bool:
        return self.find_credential(email) is not None

    def create(self, usuario: Usuario) -> Usuario:
        self._db.add(usuario)
        self._db.commit()
        self._db.refresh(usuario)
        return usuario