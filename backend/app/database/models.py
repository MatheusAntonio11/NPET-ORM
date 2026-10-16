import enum
from datetime import date, time
from decimal import Decimal

from sqlalchemy import (
    CHAR,
    Boolean,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    false,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class TipoUsuario(str, enum.Enum):
    administrador = "administrador"
    doador = "doador"
    instituicao = "instituicao"


class TipoDoacao(str, enum.Enum):
    monetaria = "monetaria"
    produto = "produto"


class StatusDoacao(str, enum.Enum):
    pendente = "pendente"
    confirmada = "confirmada"
    cancelada = "cancelada"


class FormaPagamento(str, enum.Enum):
    pix = "pix"
    cartao_credito = "cartao_credito"


class FormaEntrega(str, enum.Enum):
    visita = "visita"
    compra_parceiro = "compra_parceiro"


class Unidade(str, enum.Enum):
    unidade = "unidade"
    kg = "kg"
    g = "g"
    l = "l"
    ml = "ml"
    caixa = "caixa"
    pacote = "pacote"
    outro = "outro"


class Plataforma(str, enum.Enum):
    facebook = "facebook"
    instagram = "instagram"
    email = "email"
    linkedin = "linkedin"
    whatsapp = "whatsapp"
    site = "site"


class Prioridade(str, enum.Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"


def pg_enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    """Grava no banco o valor (ex.: 'pix'), não o nome do membro."""
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [m.value for m in e],
    )


# ---------- Models ----------

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (UniqueConstraint("provider", "provider_id"),)

    id_usuario: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(45))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    senha: Mapped[str | None] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(20), server_default="local")
    provider_id: Mapped[str | None] = mapped_column(String(100))
    telefone: Mapped[str | None] = mapped_column(String(20))
    cpf: Mapped[str | None] = mapped_column(String(11))
    tipo_usuario: Mapped[TipoUsuario] = mapped_column(
        pg_enum(TipoUsuario, "tipo_usuario")
    )

    instituicao: Mapped["Instituicao | None"] = relationship(
        back_populates="usuario", uselist=False
    )
    doacoes: Mapped[list["Doacao"]] = relationship(back_populates="usuario")


class Instituicao(Base):
    __tablename__ = "instituicoes"

    id_instituicao: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"), unique=True
    )
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(150))
    telefone: Mapped[str | None] = mapped_column(String(20))
    logo: Mapped[str | None] = mapped_column(String(255))
    cnpj: Mapped[str | None] = mapped_column(String(14), unique=True)
    cidade: Mapped[str] = mapped_column(String(100))
    uf: Mapped[str] = mapped_column(CHAR(2))
    endereco: Mapped[str | None] = mapped_column(String(255))
    descricao: Mapped[str | None] = mapped_column(String(500))
    hora_abertura: Mapped[time | None]
    hora_fechamento: Mapped[time | None]
    qtd_animais: Mapped[int | None]
    aceita_voluntarios: Mapped[bool] = mapped_column(
        Boolean, server_default=false()
    )
    aceita_doacoes: Mapped[bool] = mapped_column(
        Boolean, server_default=true()
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="instituicao")
    doacoes: Mapped[list["Doacao"]] = relationship(back_populates="instituicao")
    redes_sociais: Mapped[list["RedeSocial"]] = relationship(
        back_populates="instituicao", cascade="all, delete-orphan"
    )
    necessidades: Mapped[list["Necessidade"]] = relationship(
        back_populates="instituicao", cascade="all, delete-orphan"
    )


class Doacao(Base):
    __tablename__ = "doacoes"

    id_doacao: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"))
    id_instituicao: Mapped[int] = mapped_column(
        ForeignKey("instituicoes.id_instituicao")
    )
    tipo_doacao: Mapped[TipoDoacao] = mapped_column(
        pg_enum(TipoDoacao, "tipo_doacao")
    )
    status: Mapped[StatusDoacao] = mapped_column(
        pg_enum(StatusDoacao, "status_doacao"), server_default="pendente"
    )
    feedback_doacao: Mapped[str | None] = mapped_column(String(300))

    usuario: Mapped["Usuario"] = relationship(back_populates="doacoes")
    instituicao: Mapped["Instituicao"] = relationship(back_populates="doacoes")
    dinheiro: Mapped["DoacaoDinheiro | None"] = relationship(
        back_populates="doacao", uselist=False, cascade="all, delete-orphan"
    )
    produto: Mapped["DoacaoProduto | None"] = relationship(
        back_populates="doacao", uselist=False, cascade="all, delete-orphan"
    )


class DoacaoDinheiro(Base):
    __tablename__ = "doacoes_dinheiro"

    id_doacao_dinheiro: Mapped[int] = mapped_column(primary_key=True)
    id_doacao: Mapped[int] = mapped_column(
        ForeignKey("doacoes.id_doacao"), unique=True
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    forma_pagamento: Mapped[FormaPagamento] = mapped_column(
        pg_enum(FormaPagamento, "forma_pagamento")
    )
    recorrente: Mapped[bool] = mapped_column(Boolean, server_default=false())

    doacao: Mapped["Doacao"] = relationship(back_populates="dinheiro")


class DoacaoProduto(Base):
    __tablename__ = "doacoes_produto"

    id_doacao_produto: Mapped[int] = mapped_column(primary_key=True)
    id_doacao: Mapped[int] = mapped_column(
        ForeignKey("doacoes.id_doacao"), unique=True
    )
    forma_entrega: Mapped[FormaEntrega] = mapped_column(
        pg_enum(FormaEntrega, "forma_entrega")
    )

    doacao: Mapped["Doacao"] = relationship(back_populates="produto")
    itens: Mapped[list["ItemDoacaoProduto"]] = relationship(
        back_populates="doacao_produto", cascade="all, delete-orphan"
    )
    visita: Mapped["Visita | None"] = relationship(
        back_populates="doacao_produto",
        uselist=False,
        cascade="all, delete-orphan",
    )


class ItemDoacaoProduto(Base):
    __tablename__ = "itens_doacao_produto"

    id_item_doacao: Mapped[int] = mapped_column(primary_key=True)
    id_doacao_produto: Mapped[int] = mapped_column(
        ForeignKey("doacoes_produto.id_doacao_produto")
    )
    nome_produto: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(String(255))
    quantidade: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    unidade: Mapped[Unidade] = mapped_column(pg_enum(Unidade, "unidade"))

    doacao_produto: Mapped["DoacaoProduto"] = relationship(back_populates="itens")


class Visita(Base):
    __tablename__ = "visitas"

    id_visita: Mapped[int] = mapped_column(primary_key=True)
    id_doacao_produto: Mapped[int] = mapped_column(
        ForeignKey("doacoes_produto.id_doacao_produto"), unique=True
    )
    data_visita: Mapped[date]
    hora_visita: Mapped[time]

    doacao_produto: Mapped["DoacaoProduto"] = relationship(back_populates="visita")


class RedeSocial(Base):
    __tablename__ = "redes_sociais"
    __table_args__ = (UniqueConstraint("id_instituicao", "plataforma"),)

    id_rede_social: Mapped[int] = mapped_column(primary_key=True)
    id_instituicao: Mapped[int] = mapped_column(
        ForeignKey("instituicoes.id_instituicao")
    )
    plataforma: Mapped[Plataforma] = mapped_column(pg_enum(Plataforma, "plataforma"))
    contato: Mapped[str] = mapped_column(String(255))

    instituicao: Mapped["Instituicao"] = relationship(back_populates="redes_sociais")


class Necessidade(Base):
    __tablename__ = "necessidades"

    id_necessidade: Mapped[int] = mapped_column(primary_key=True)
    id_instituicao: Mapped[int] = mapped_column(
        ForeignKey("instituicoes.id_instituicao")
    )
    nome_item: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(String(255))
    prioridade: Mapped[Prioridade] = mapped_column(pg_enum(Prioridade, "prioridade"))
    quantidade_meta: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    unidade: Mapped[Unidade | None] = mapped_column(pg_enum(Unidade, "unidade"))

    instituicao: Mapped["Instituicao"] = relationship(back_populates="necessidades")