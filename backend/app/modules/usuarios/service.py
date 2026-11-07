from collections.abc import Sequence

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.security import hash_password
from app.database.models import TipoUsuario, Usuario
from app.database.schemas import UsuarioUpdate
from app.modules.usuarios.repository import UsuarioRepository


class UsuarioService:
    def __init__(self, repository: UsuarioRepository) -> None:
        self._repository = repository

    @staticmethod
    def _is_admin(user: Usuario) -> bool:
        return user.tipo_usuario == TipoUsuario.administrador

    def _check_access(self, current_user: Usuario, id_usuario: int) -> None:
        if not self._is_admin(current_user) and current_user.id_usuario != id_usuario:
            raise ForbiddenError("Você não tem permissão para acessar este usuário.")

    def list_users(self, skip: int, limit: int) -> Sequence[Usuario]:
        return self._repository.list_all(skip, limit)

    def get_user(self, id_usuario: int, current_user: Usuario) -> Usuario:
        self._check_access(current_user, id_usuario)
        usuario = self._repository.get_by_id(id_usuario)
        if usuario is None:
            raise NotFoundError("Usuário não encontrado.")
        return usuario

    def update_user(
        self, id_usuario: int, data: UsuarioUpdate, current_user: Usuario
    ) -> Usuario:
        usuario = self.get_user(id_usuario, current_user)
        changes = data.model_dump(exclude_none=True)

        new_email = changes.get("email")
        if new_email and new_email != usuario.email:
            if self._repository.email_exists(new_email):
                raise ConflictError("E-mail já cadastrado.")

        new_cpf = changes.get("cpf")
        if new_cpf and str(new_cpf) != str(usuario.cpf):
            if self._repository.cpf_exists(str(new_cpf)):
                raise ConflictError("CPF já cadastrado.")

        if "senha" in changes:
            changes["senha"] = hash_password(changes["senha"])

        for field, value in changes.items():
            setattr(usuario, field, value)

        return self._repository.update(usuario)

    def delete_user(self, id_usuario: int, current_user: Usuario) -> None:
        usuario = self.get_user(id_usuario, current_user)
        self._repository.delete(usuario)