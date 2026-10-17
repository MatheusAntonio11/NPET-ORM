"""
Rotas REST de Autenticação (camada Controller)

Só cuida de HTTP: recebe o DTO já validado pelo schema, chama o Service e devolve a resposta.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import LoginRequest, UsuarioCreate, UsuarioOut
from app.modules.auth.usuarios.repository import AuthRepository
from app.modules.auth.usuarios.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/register", response_model=UsuarioOut, status_code=201)
def register(data: UsuarioCreate, service: AuthService = Depends(get_auth_service)):
    return service.register(data)


@router.post("/login")
def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return {"message": service.login(data.email, data.senha)}