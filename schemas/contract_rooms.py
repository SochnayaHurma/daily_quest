from pydantic import BaseModel, Field

from schemas.contract import PublicContractDetail


class SimplePublicRoom(BaseModel):
    id: int
    name: str


class PublicContractRooms(BaseModel):
    contract: PublicContractDetail | None = None
    contract_relations: list[SimplePublicRoom] = Field(default_factory=list)
    no_relations: list[SimplePublicRoom] = Field(default_factory=list)


class AddContractRoom(BaseModel):
    contract_id: int
    room_id: int


class DropContractRoom(AddContractRoom):
    contract_id: int
    room_id: int
