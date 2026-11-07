from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic.alias_generators import to_camel

if TYPE_CHECKING:
    from app.database.models import Instituicao


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RedesSociais(CamelModel):
    facebook: str | None = None
    instagram: str | None = None
    email: str | None = None
    linkedin: str | None = None
    whatsapp: str | None = None
    site: str | None = None


class InstituicaoCreate(CamelModel):
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=20)
    logo: str | None = Field(default=None, max_length=255)
    cnpj: str | None = Field(default=None, pattern=r"^\d{14}$")
    cidade: str = Field(min_length=1, max_length=100)
    uf: str = Field(min_length=2, max_length=2)
    endereco: str | None = Field(default=None, max_length=255)
    descricao: str | None = Field(default=None, max_length=500)
    hora_abertura: time | None = None
    hora_fechamento: time | None = None
    qtd_animais: int | None = Field(default=None, ge=0)
    aceita_voluntarios: bool = False
    aceita_doacoes: bool = True

    @field_validator("uf")
    @classmethod
    def uf_maiuscula(cls, v: str) -> str:
        return v.upper()


class InstituicaoUpdate(CamelModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=20)
    logo: str | None = Field(default=None, max_length=255)
    cnpj: str | None = Field(default=None, pattern=r"^\d{14}$")
    cidade: str | None = Field(default=None, min_length=1, max_length=100)
    uf: str | None = Field(default=None, min_length=2, max_length=2)
    endereco: str | None = Field(default=None, max_length=255)
    descricao: str | None = Field(default=None, max_length=500)
    hora_abertura: time | None = None
    hora_fechamento: time | None = None
    qtd_animais: int | None = Field(default=None, ge=0)
    aceita_voluntarios: bool | None = None
    aceita_doacoes: bool | None = None

    @field_validator("uf")
    @classmethod
    def uf_maiuscula(cls, v: str | None) -> str | None:
        return v.upper() if v else v


class InstituicaoResponse(CamelModel):
    id: int
    nome: str
    logo: str | None = None
    cnpj: str | None = None
    email: str | None = None
    telefone: str | None = None
    cidade: str
    uf: str
    endereco: str | None = None
    animais_sob_cuidado: int | None = None
    horario_funcionamento: str | None = None
    descricao: str | None = None
    principais_necessidades: str | None = None
    aceita_voluntarios: bool | None = None
    aceita_doacoes: bool
    redes_sociais: RedesSociais | None = None

    @classmethod
    def from_model(cls, i: Instituicao) -> InstituicaoResponse:
        horario = None
        if i.hora_abertura and i.hora_fechamento:
            horario = f"{i.hora_abertura:%H:%M} - {i.hora_fechamento:%H:%M}"

        return cls(
            id=i.id_instituicao,
            nome=i.nome,
            logo=i.logo,
            cnpj=i.cnpj,
            email=i.email,
            telefone=i.telefone,
            cidade=i.cidade,
            uf=i.uf,
            endereco=i.endereco,
            animais_sob_cuidado=i.qtd_animais,
            horario_funcionamento=horario,
            descricao=i.descricao,
            aceita_voluntarios=i.aceita_voluntarios,
            aceita_doacoes=i.aceita_doacoes,
        )