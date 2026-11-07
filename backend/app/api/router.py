from fastapi import APIRouter

from app.health.router import router as health_router
from app.modules.auth.usuarios.router import auth_router
from app.modules.auth.usuarios.router import router as users_auth_router
from app.modules.usuarios.router import users_router
from app.modules.auth.instituicoes.router import router as institutions_auth_router
from app.modules.instituicoes.router import router as instituicoes_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_auth_router)
api_router.include_router(users_router)
api_router.include_router(institutions_auth_router)
api_router.include_router(instituicoes_router)
