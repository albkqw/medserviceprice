from typing import Generic, TypeVar

from pydantic import BaseModel

ItemT = TypeVar("ItemT")


class PaginatedResponse(BaseModel, Generic[ItemT]):
    total: int
    limit: int
    offset: int
    items: list[ItemT]
