"""
Regras de negócio de Autenticação (camada Service)

Não conhece HTTP nem sabe onde os dados estão guardados: pede ao Repository a credencial e decide se a autenticação é válida.
"""

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.database.models import TipoUsuario, Usuario
from app.database.schemas import UsuarioCreate
from app.modules.auth.usuarios.repository import AuthRepository


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repository = repository

    def login(self, email: str, password: str) -> str:
        usuario = self._repository.find_credential(email)

        if usuario is None or usuario.senha is None:
            raise UnauthorizedError("E-mail ou senha inválidos.")

        if not verify_password(password, usuario.senha):
            raise UnauthorizedError("E-mail ou senha inválidos.")

        return "Autenticação realizada com sucesso."

    def register(self, data: UsuarioCreate) -> Usuario:
        if data.tipo_usuario == TipoUsuario.administrador:
            raise UnauthorizedError("Não é permitido criar administradores por este cadastro.")

        if self._repository.email_exists(data.email):
            raise ConflictError("E-mail já cadastrado.")

        usuario = Usuario(
            nome=data.nome,
            email=data.email,
            senha=hash_password(data.senha),
            telefone=data.telefone,
            cpf=data.cpf,
            tipo_usuario=data.tipo_usuario,
        )
        return self._repository.create(usuario)