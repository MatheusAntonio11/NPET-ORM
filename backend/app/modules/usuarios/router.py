from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.database.database import get_db
from app.database.models import Usuario
from app.database.schemas import UsuarioOut, UsuarioUpdate
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.service import UsuarioService

users_router = APIRouter(prefix="/users", tags=["users"])


def get_usuario_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(UsuarioRepository(db))


@users_router.get("", response_model=list[UsuarioOut], summary="Lista usuários (admin)")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    _: Usuario = Depends(require_admin),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.list_users(skip, limit)


@users_router.get("/me", response_model=UsuarioOut, summary="Dados do usuário logado")
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@users_router.patch("/me", response_model=UsuarioOut, summary="Atualiza o usuário logado")
def update_me(
    data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.update_user(current_user.id_usuario, data, current_user)


@users_router.delete("/me", status_code=204, summary="Exclui o usuário logado")
def delete_me(
    current_user: Usuario = Depends(get_current_user),
    service: UsuarioService = Depends(get_usuario_service),
):
    service.delete_user(current_user.id_usuario, current_user)
    return Response(status_code=204)


@users_router.get("/{id_usuario}", response_model=UsuarioOut)
def get_user(
    id_usuario: int,
    current_user: Usuario = Depends(get_current_user),
    service: UsuarioService = Depends(get_usuario_service),
):
    return service.get_user(id_usuario, current_user)


@users_router.patch("/{id_usuario}", response_model=UsuarioOut)
def update_user(
    id_usuario: int,
    data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    _: Usuario = Depends(require_admin),

    service: UsuarioService = Depends(get_usuario_service),
):
    return service.update_user(id_usuario, data, current_user)


@users_router.delete("/{id_usuario}", status_code=204)
def delete_user(
    id_usuario: int,
    current_user: Usuario = Depends(get_current_user),
    _: Usuario = Depends(require_admin),
    service: UsuarioService = Depends(get_usuario_service),
):
    service.delete_user(id_usuario, current_user)
    return Response(status_code=204)