from fastapi import APIRouter, Response, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.schemas import LoginRequest, LoginResponse, UsuarioCreate, UsuarioOut
from app.modules.auth.usuarios.repository import AuthRepository
from app.modules.auth.usuarios.service import AuthService

router = APIRouter(prefix="/auth", tags=["users-auth"])
auth_router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/register", response_model=UsuarioOut, status_code=201)
def register(data: UsuarioCreate, service: AuthService = Depends(get_auth_service)):
    return service.register(data)


@auth_router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, response: Response, service: AuthService = Depends(get_auth_service)):
    result = service.login(data.email, data.senha)
    response.set_cookie(
        "access_token",
        result.access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # True em produção (HTTPS)
        max_age=60 * 60,
    )
    return result

from app.core.dependencies import ACCESS_TOKEN_COOKIE

@auth_router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(ACCESS_TOKEN_COOKIE)
    response.status_code = 204
    return response


#@auth_router.post("/token", response_model=LoginResponse, summary="Login via formulário OAuth2 (usado pelo Authorize do Swagger)")
#def token(form: OAuth2PasswordRequestForm = Depends(), service: AuthService = Depends(get_auth_service)):
#    return service.login(form.email, form.senha)*/
