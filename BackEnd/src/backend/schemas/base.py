from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class SchemaBase(BaseModel):
    """Base comun: acepta snake_case y responde siempre en camelCase."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class RespuestaPaginada(SchemaBase, Generic[T]):
    items: list[T]
    total: int
    pagina: int
    tamano_pagina: int = Field(alias="tamanoPagina")
