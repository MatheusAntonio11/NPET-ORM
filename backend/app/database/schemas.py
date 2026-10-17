from datetime import date, time
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.database.models import (
    FormaEntrega,
    FormaPagamento,
    Plataforma,
    Prioridade,
    StatusDoacao,
    TipoDoacao,
    TipoUsuario,
    Unidade,
)

# ---------- Tipos reutilizáveis ----------

CPF = Annotated[str, Field(pattern=r"^\d{11}$", description="11 dígitos, sem pontuação")]
CNPJ = Annotated[str, Field(pattern=r"^\d{14}$", description="14 dígitos, sem pontuação")]
UF = Annotated[str, Field(pattern=r"^[A-Z]{2}$", description="Sigla em maiúsculo, ex.: GO")]


class ORMBase(BaseModel):
    """Base para schemas de saída (leem objetos SQLAlchemy)."""

    model_config = ConfigDict(from_attributes=True)


# =====================================================================
# Usuário
# =====================================================================

class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=45)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72)  # texto puro; gerar hash na rota
    telefone: str | None = Field(default=None, max_length=20)
    cpf: CPF | None = None
    tipo_usuario: TipoUsuario


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=45)
    telefone: str | None = Field(default=None, max_length=20)
    cpf: CPF | None = None


class UsuarioOut(ORMBase):
    id_usuario: int
    nome: str
    email: EmailStr
    telefone: str | None
    cpf: str | None
    provider: str
    tipo_usuario: TipoUsuario
    # senha e provider_id ficam de fora de propósito


# =====================================================================
# Rede social
# =====================================================================

class RedeSocialCreate(BaseModel):
    plataforma: Plataforma
    contato: str = Field(min_length=1, max_length=255)


class RedeSocialUpdate(BaseModel):
    contato: str = Field(min_length=1, max_length=255)


class RedeSocialOut(ORMBase):
    id_rede_social: int
    id_instituicao: int
    plataforma: Plataforma
    contato: str


# =====================================================================
# Necessidade
# =====================================================================

class NecessidadeCreate(BaseModel):
    nome_item: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=255)
    prioridade: Prioridade
    quantidade_meta: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)
    unidade: Unidade | None = None


class NecessidadeUpdate(BaseModel):
    nome_item: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=255)
    prioridade: Prioridade | None = None
    quantidade_meta: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)
    unidade: Unidade | None = None


class NecessidadeOut(ORMBase):
    id_necessidade: int
    id_instituicao: int
    nome_item: str
    descricao: str | None
    prioridade: Prioridade
    quantidade_meta: Decimal | None
    unidade: Unidade | None


# =====================================================================
# Instituição
# =====================================================================

class InstituicaoCreate(BaseModel):
    id_usuario: int  # depois, pegar do usuário autenticado
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=20)
    logo: str | None = Field(default=None, max_length=255)
    cnpj: CNPJ | None = None
    cidade: str = Field(min_length=1, max_length=100)
    uf: UF
    endereco: str | None = Field(default=None, max_length=255)
    descricao: str | None = Field(default=None, max_length=500)
    hora_abertura: time | None = None
    hora_fechamento: time | None = None
    qtd_animais: int | None = Field(default=None, ge=0)
    aceita_voluntarios: bool = False
    aceita_doacoes: bool = True


class InstituicaoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=20)
    logo: str | None = Field(default=None, max_length=255)
    cnpj: CNPJ | None = None
    cidade: str | None = Field(default=None, min_length=1, max_length=100)
    uf: UF | None = None
    endereco: str | None = Field(default=None, max_length=255)
    descricao: str | None = Field(default=None, max_length=500)
    hora_abertura: time | None = None
    hora_fechamento: time | None = None
    qtd_animais: int | None = Field(default=None, ge=0)
    aceita_voluntarios: bool | None = None
    aceita_doacoes: bool | None = None


class InstituicaoOut(ORMBase):
    id_instituicao: int
    id_usuario: int
    nome: str
    email: EmailStr | None
    telefone: str | None
    logo: str | None
    cnpj: str | None
    cidade: str
    uf: str
    endereco: str | None
    descricao: str | None
    hora_abertura: time | None
    hora_fechamento: time | None
    qtd_animais: int | None
    aceita_voluntarios: bool
    aceita_doacoes: bool


class InstituicaoDetalhe(InstituicaoOut):
    """Instituição com redes sociais e necessidades (use selectinload na query)."""

    redes_sociais: list[RedeSocialOut] = []
    necessidades: list[NecessidadeOut] = []


# =====================================================================
# Doação
# =====================================================================

class DoacaoDinheiroCreate(BaseModel):
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    forma_pagamento: FormaPagamento
    recorrente: bool = False


class DoacaoDinheiroOut(ORMBase):
    id_doacao_dinheiro: int
    valor: Decimal
    forma_pagamento: FormaPagamento
    recorrente: bool


class ItemDoacaoCreate(BaseModel):
    nome_produto: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=255)
    quantidade: Decimal = Field(gt=0, max_digits=8, decimal_places=2)
    unidade: Unidade


class ItemDoacaoOut(ORMBase):
    id_item_doacao: int
    nome_produto: str
    descricao: str | None
    quantidade: Decimal
    unidade: Unidade


class VisitaCreate(BaseModel):
    data_visita: date
    hora_visita: time


class VisitaOut(ORMBase):
    id_visita: int
    data_visita: date
    hora_visita: time


class DoacaoProdutoCreate(BaseModel):
    forma_entrega: FormaEntrega
    itens: list[ItemDoacaoCreate] = Field(min_length=1)
    visita: VisitaCreate | None = None

    @model_validator(mode="after")
    def validar_visita(self):
        if self.forma_entrega == FormaEntrega.visita and self.visita is None:
            raise ValueError("Informe data e hora da visita quando a forma de entrega for 'visita'")
        if self.forma_entrega != FormaEntrega.visita and self.visita is not None:
            raise ValueError("Visita só se aplica quando a forma de entrega for 'visita'")
        return self


class DoacaoProdutoOut(ORMBase):
    id_doacao_produto: int
    forma_entrega: FormaEntrega
    itens: list[ItemDoacaoOut] = []
    visita: VisitaOut | None = None


class DoacaoCreate(BaseModel):
    id_usuario: int  # depois, pegar do usuário autenticado
    id_instituicao: int
    tipo_doacao: TipoDoacao
    feedback_doacao: str | None = Field(default=None, max_length=300)
    dinheiro: DoacaoDinheiroCreate | None = None
    produto: DoacaoProdutoCreate | None = None

    @model_validator(mode="after")
    def validar_tipo(self):
        if self.tipo_doacao == TipoDoacao.monetaria:
            if self.dinheiro is None or self.produto is not None:
                raise ValueError("Doação monetária exige 'dinheiro' e não aceita 'produto'")
        else:
            if self.produto is None or self.dinheiro is not None:
                raise ValueError("Doação de produto exige 'produto' e não aceita 'dinheiro'")
        return self


class DoacaoStatusUpdate(BaseModel):
    status: StatusDoacao
    feedback_doacao: str | None = Field(default=None, max_length=300)


class DoacaoOut(ORMBase):
    id_doacao: int
    id_usuario: int
    id_instituicao: int
    tipo_doacao: TipoDoacao
    status: StatusDoacao
    feedback_doacao: str | None
    dinheiro: DoacaoDinheiroOut | None = None
    produto: DoacaoProdutoOut | None = None

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str