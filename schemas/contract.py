from pydantic import BaseModel, Field


class CreateContract(BaseModel):
    name: str = Field(min_length=3, max_length=15)
    editable_tasks: int = Field(ge=0, le=6)


class EditContract(BaseModel):
    id: int = Field(ge=1)
    name: str = Field(min_length=3, max_length=15)
    editable_tasks: int = Field(ge=1, le=6)


class PublicContractDetail(BaseModel):
    id: int
    name: str
    editable_tasks: int
    active: bool = False

    def __hash__(self):
        return hash((self.id, self.name))


class PublicContract(BaseModel):
    current_contract: PublicContractDetail
    contracts: list[PublicContractDetail]

