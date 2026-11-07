from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database.database import get_db
from app.database.models import TipoUsuario, Usuario

ACCESS_TOKEN_COOKIE = "access_token"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


def get_current_user(
    request: Request,
    bearer_token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    token = bearer_token or request.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise UnauthorizedError("Não autenticado.")

    id_usuario = decode_access_token(token)

    usuario = db.get(Usuario, id_usuario)
    if usuario is None:
        raise UnauthorizedError("Usuário não encontrado.")
    return usuario


def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if current_user.tipo_usuario != TipoUsuario.administrador:
        raise ForbiddenError("Acesso restrito a administradores.")
    return current_user