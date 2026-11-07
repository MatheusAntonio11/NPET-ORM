from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.database.models import Usuario
from app.modules.instituicoes.repository import InstituicaoRepository
from app.modules.instituicoes.schemas import (
    InstituicaoCreate,
    InstituicaoResponse,
    InstituicaoUpdate,
)
from app.modules.instituicoes.service import InstituicaoService

router = APIRouter(
    prefix="/instituicoes",
    tags=["instituicoes"],
    dependencies=[Depends(get_current_user)],
)


def get_service(db: Session = Depends(get_db)) -> InstituicaoService:
    return InstituicaoService(InstituicaoRepository(db))


@router.get(
    "",
    response_model=list[InstituicaoResponse],
    response_model_exclude_none=True,
    summary="Lista as instituições",
)
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    service: InstituicaoService = Depends(get_service),
):
    return [InstituicaoResponse.from_model(i) for i in service.list_instituicoes(skip, limit)]


@router.get(
    "/me",
    response_model=InstituicaoResponse,
    response_model_exclude_none=True,
    summary="Instituição do usuário logado",
)
def minha_instituicao(
    current_user: Usuario = Depends(get_current_user),
    service: InstituicaoService = Depends(get_service),
):
    return InstituicaoResponse.from_model(service.get_minha_instituicao(current_user))


@router.get(
    "/{instituicao_id}",
    response_model=InstituicaoResponse,
    response_model_exclude_none=True,
    summary="Busca uma instituição pelo id",
)
def buscar_por_id(instituicao_id: int, service: InstituicaoService = Depends(get_service)):
    return InstituicaoResponse.from_model(service.get_instituicao(instituicao_id))


@router.post(
    "",
    response_model=InstituicaoResponse,
    response_model_exclude_none=True,
    status_code=201,
    summary="Cadastra a instituição do usuário logado",
)
def criar(
    data: InstituicaoCreate,
    current_user: Usuario = Depends(get_current_user),
    service: InstituicaoService = Depends(get_service),
):
    return InstituicaoResponse.from_model(service.create_instituicao(data, current_user))


@router.patch(
    "/{instituicao_id}",
    response_model=InstituicaoResponse,
    response_model_exclude_none=True,
    summary="Atualiza uma instituição (dono ou admin)",
)
def atualizar(
    instituicao_id: int,
    data: InstituicaoUpdate,
    current_user: Usuario = Depends(get_current_user),
    service: InstituicaoService = Depends(get_service),
):
    return InstituicaoResponse.from_model(
        service.update_instituicao(instituicao_id, data, current_user)
    )


@router.delete(
    "/{instituicao_id}",
    status_code=204,
    summary="Exclui uma instituição (dono ou admin)",
)
def excluir(
    instituicao_id: int,
    current_user: Usuario = Depends(get_current_user),
    service: InstituicaoService = Depends(get_service),
):
    service.delete_instituicao(instituicao_id, current_user)
    return Response(status_code=204)