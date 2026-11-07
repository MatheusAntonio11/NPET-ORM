from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.core.exceptions import ForbiddenError
from app.core.security import JWT_ALGORITHM, decode_access_token
from app.database.models import TipoUsuario, Usuario
from app.modules.auth.dependencies import require_role

API = "/api/v1"


def corpo_de_cadastro(tipo_usuario: str, email: str) -> tuple[str, dict]:
    if tipo_usuario == "instituicao":
        return "institutions", {"nome": "ASPAAN", "email": email, "senha": "senha1234", "cidade": "Anápolis", "uf": "GO"}
    return "users", {"nome": "Teste", "email": email, "senha": "senha1234", "tipo_usuario": tipo_usuario}


def cadastrar_e_logar(client, tipo_usuario: str) -> dict:
    email = f"{tipo_usuario}@npet.org"
    prefixo, corpo = corpo_de_cadastro(tipo_usuario, email)
    assert client.post(f"{API}/{prefixo}/auth/register", json=corpo).status_code == 201
    resposta = client.post(f"{API}/auth/login", json={"email": email, "senha": "senha1234"})
    assert resposta.status_code == 200
    return resposta.json()


def gerar_token(sub: str, minutos: int) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=minutos)
    return jwt.encode({"sub": sub, "exp": expira_em}, settings.JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def test_sem_token_retorna_401(client):
    assert client.get(f"{API}/instituicoes").status_code == 401


@pytest.mark.parametrize("token", [
    "token-qualquer",
    jwt.encode({"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, "outra-chave", algorithm=JWT_ALGORITHM),
])
def test_token_invalido_retorna_401(client, token):
    resposta = client.get(f"{API}/instituicoes", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_token_expirado_retorna_401(client):
    cadastrar_e_logar(client, "doador")
    token = gerar_token("1", minutos=-1)
    resposta = client.get(f"{API}/instituicoes", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_token_de_usuario_inexistente_retorna_401(client):
    token = gerar_token("999", minutos=5)
    resposta = client.get(f"{API}/instituicoes", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_login_com_senha_errada_retorna_401(client):
    cadastrar_e_logar(client, "doador")
    resposta = client.post(f"{API}/auth/login", json={"email": "doador@npet.org", "senha": "errada123"})
    assert resposta.status_code == 401


@pytest.mark.parametrize("tipo_usuario", ["doador", "instituicao"])
def test_login_unico_devolve_token_e_role(client, tipo_usuario):
    resposta = cadastrar_e_logar(client, tipo_usuario)

    assert resposta["token_type"] == "bearer"
    assert resposta["tipo_usuario"] == tipo_usuario
    assert jwt.decode(resposta["access_token"], settings.JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])["tipo_usuario"] == tipo_usuario


@pytest.mark.parametrize("tipo_usuario", ["doador", "instituicao"])
def test_token_valido_acessa_rotas_protegidas(client, tipo_usuario):
    headers = {"Authorization": f"Bearer {cadastrar_e_logar(client, tipo_usuario)['access_token']}"}

    lista = client.get(f"{API}/instituicoes", headers=headers)
    assert lista.status_code == 200
    assert len(lista.json()) > 0

    assert client.get(f"{API}/instituicoes/1", headers=headers).status_code == 200


@pytest.mark.parametrize("tipo_usuario", ["doador", "instituicao"])
def test_login_por_formulario_oauth2(client, tipo_usuario):
    cadastrar_e_logar(client, tipo_usuario)

    resposta = client.post(f"{API}/auth/token", data={"username": f"{tipo_usuario}@npet.org", "password": "senha1234"})
    assert resposta.status_code == 200
    assert resposta.json()["tipo_usuario"] == tipo_usuario
    assert decode_access_token(resposta.json()["access_token"]) == 1


@pytest.mark.parametrize("rota", ["users/auth/login", "institutions/auth/login"])
def test_logins_antigos_foram_removidos(client, rota):
    resposta = client.post(f"{API}/{rota}", json={"email": "x@npet.org", "senha": "senha1234"})
    assert resposta.status_code == 404


def test_require_role_bloqueia_tipo_nao_permitido():
    somente_instituicao = require_role(TipoUsuario.instituicao)

    assert somente_instituicao(Usuario(tipo_usuario=TipoUsuario.instituicao)).tipo_usuario == TipoUsuario.instituicao

    with pytest.raises(ForbiddenError):
        somente_instituicao(Usuario(tipo_usuario=TipoUsuario.doador))


def test_cadastro_de_instituicao_cria_usuario_e_perfil(client, session_factory):
    resposta = client.post(f"{API}/institutions/auth/register", json={
        "nome": "ASPAAN", "email": "aspaan@npet.org", "senha": "senha1234",
        "cnpj": "11102088000179", "cidade": "Anápolis", "uf": "GO",
    })
    assert resposta.status_code == 201
    assert resposta.json()["tipo_usuario"] == "instituicao"

    with session_factory() as db:
        usuario = db.scalar(select(Usuario).where(Usuario.email == "aspaan@npet.org"))
        assert usuario.instituicao is not None
        assert usuario.instituicao.id_usuario == usuario.id_usuario
        assert (usuario.instituicao.cidade, usuario.instituicao.uf, usuario.instituicao.cnpj) == ("Anápolis", "GO", "11102088000179")


@pytest.mark.parametrize("campo, valor", [("email", "aspaan@npet.org"), ("cnpj", "11102088000179")])
def test_cadastro_de_instituicao_duplicado_retorna_409(client, campo, valor):
    corpo = {"nome": "ASPAAN", "email": "aspaan@npet.org", "senha": "senha1234",
             "cnpj": "11102088000179", "cidade": "Anápolis", "uf": "GO"}
    assert client.post(f"{API}/institutions/auth/register", json=corpo).status_code == 201

    outro = {**corpo, "email": "outra@npet.org", "cnpj": "99999999000199", campo: valor}
    assert client.post(f"{API}/institutions/auth/register", json=outro).status_code == 409


def test_senha_acima_de_72_bytes_retorna_422(client):
    resposta = client.post(f"{API}/users/auth/register", json={
        "nome": "Teste", "email": "acento@npet.org", "senha": "ç" * 40, "tipo_usuario": "doador",
    })
    assert resposta.status_code == 422
