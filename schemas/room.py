from typing import Optional

from pydantic import BaseModel, Field

from schemas.task import PublicTask


class CreateRoom(BaseModel):
    contract_id: int
    name: str = Field(min_length=3, max_length=50)


class PublicRoom(BaseModel):
    id: Optional[int] = None
    name: str
    coins: int = 0
    tasks: list[PublicTask] = Field(default_factory=list)