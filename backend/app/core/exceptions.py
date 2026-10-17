"""
Exceções de domínio da aplicação.

Os Services lançam estas exceções; um handler global em `app.main` as converte em respostas HTTP JSON padronizadas. Assim as camadas de negócio não precisam conhecer detalhes de HTTP.
"""

class AppError(Exception):
    """Erro base da aplicação."""

    status_code: int = 400

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409