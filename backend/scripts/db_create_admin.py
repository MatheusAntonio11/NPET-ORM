import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.database.database import SessionLocal
from app.database.models import TipoUsuario, Usuario


def main() -> None:
    nome = input("Nome: ").strip()
    email = input("E-mail: ").strip()
    cpf = input("CPF: ").strip()
    telefone = input("Telefone (opcional): ").strip() or None
    senha = input("Senha: ").strip()

    with SessionLocal() as db:
        if db.scalar(select(Usuario).where(Usuario.email == email)):
            print("Já existe um usuário com esse e-mail.")
            return

        db.add(
            Usuario(
                nome=nome,
                email=email,
                senha=hash_password(senha),
                telefone=telefone,
                cpf=cpf,
                tipo_usuario=TipoUsuario.administrador,
            )
        )
        db.commit()
        print("Administrador criado.")


if __name__ == "__main__":
    main()