from collections.abc import Sequence

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.database.models import Instituicao, TipoUsuario, Usuario
from app.modules.instituicoes.repository import InstituicaoRepository
from app.modules.instituicoes.schemas import InstituicaoCreate, InstituicaoUpdate


class InstituicaoService:
    def __init__(self, repository: InstituicaoRepository) -> None:
        self._repository = repository

    @staticmethod
    def _is_admin(user: Usuario) -> bool:
        return user.tipo_usuario == TipoUsuario.administrador

    def _check_owner_or_admin(self, instituicao: Instituicao, current_user: Usuario) -> None:
        if not self._is_admin(current_user) and instituicao.id_usuario != current_user.id_usuario:
            raise ForbiddenError("Você não tem permissão para alterar esta instituição.")

    def list_instituicoes(self, skip: int, limit: int) -> Sequence[Instituicao]:
        return self._repository.list_all(skip, limit)

    def get_instituicao(self, id_instituicao: int) -> Instituicao:
        instituicao = self._repository.get_by_id(id_instituicao)
        if instituicao is None:
            raise NotFoundError("Instituição não encontrada.")
        return instituicao

    def get_minha_instituicao(self, current_user: Usuario) -> Instituicao:
        instituicao = self._repository.get_by_user_id(current_user.id_usuario)
        if instituicao is None:
            raise NotFoundError("Você ainda não possui uma instituição cadastrada.")
        return instituicao

    def create_instituicao(self, data: InstituicaoCreate, current_user: Usuario) -> Instituicao:
        if current_user.tipo_usuario != TipoUsuario.instituicao:
            raise ForbiddenError(
                "Apenas usuários do tipo instituição podem cadastrar uma instituição."
            )

        if self._repository.get_by_user_id(current_user.id_usuario) is not None:
            raise ConflictError("Este usuário já possui uma instituição cadastrada.")

        if data.cnpj and self._repository.cnpj_exists(data.cnpj):
            raise ConflictError("CNPJ já cadastrado.")

        instituicao = Instituicao(
            id_usuario=current_user.id_usuario,
            **data.model_dump(),
        )
        return self._repository.create(instituicao)

    def update_instituicao(
        self, id_instituicao: int, data: InstituicaoUpdate, current_user: Usuario
    ) -> Instituicao:
        instituicao = self.get_instituicao(id_instituicao)
        self._check_owner_or_admin(instituicao, current_user)

        changes = data.model_dump(exclude_none=True)

        new_cnpj = changes.get("cnpj")
        if new_cnpj and new_cnpj != instituicao.cnpj:
            if self._repository.cnpj_exists(new_cnpj):
                raise ConflictError("CNPJ já cadastrado.")

        for field, value in changes.items():
            setattr(instituicao, field, value)

        return self._repository.update(instituicao)

    def delete_instituicao(self, id_instituicao: int, current_user: Usuario) -> None:
        instituicao = self.get_instituicao(id_instituicao)
        self._check_owner_or_admin(instituicao, current_user)
        self._repository.delete(instituicao)