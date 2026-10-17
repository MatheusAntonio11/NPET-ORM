# Como rodar o backend NPET (modo desenvolvimento)

Pré-requisito: **Python 3.10+** (testado com 3.11.9).

## 1. Criar e ativar o ambiente virtual:

```bash
# criar
python -m venv .venv

# ativar (Windows, PowerShell)
.venv\Scripts\Activate.ps1

# ativar (Windows, CMD)
.venv\Scripts\activate.bat
```

> Se o PowerShell recusar rodar `Activate.ps1` (erro de "execution policy"),
> use o `activate.bat` pelo CMD, ou simplesmente chame os executáveis de
> dentro de `.venv\Scripts\` diretamente, sem ativar (ex.:
> `.venv\Scripts\python.exe -m uvicorn app.main:app --reload`).

## 2. Instalar as dependências:

```bash
pip install -r requirements.txt
```

## 3. Configurar variáveis de ambiente:

```bash
copy .env.example .env
```
## Criação do banco de dados, caso não tenha
```bash
alembic revision --autogenerate -m "schema inicial"
python -m alembic upgrade head 
```

## 4. Rodar a aplicação com hot-reload:

```bash
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`.

## 5. Acessar a documentação automática (Swagger):

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Healthcheck: http://localhost:8000/api/v1/health

## 6. Testar o login:

### Como usuário:

Credencial hardcoded (ver [app/modules/auth/usuarios/fake_db.py](app/modules/auth/usuarios/fake_db.py)):

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"doador@email.com.br\", \"password\": \"senha123\"}"
```

### Como instituição:

Credencial hardcoded (ver [app/modules/auth/instituicoes/fake_db.py](app/modules/auth/instituicoes/fake_db.py)):

```bash
curl -X POST http://localhost:8000/api/v1/institutions/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"instituicao@email.com.br\", \"password\": \"senha123\"}"
```

Nos dois casos: credencial certa → `200` com `{"success": true, "message": "Autenticação realizada com sucesso."}`; credencial errada → `401`.
