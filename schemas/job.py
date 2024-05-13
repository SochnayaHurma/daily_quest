from pydantic import BaseModel, Field


class CreateJob(BaseModel):
    contract_id: int
    name: str = Field(min_length=3, max_length=50)
    point: int = Field(ge=1, le=60000)
    default: bool = False


class PublicJob(BaseModel):
    id: int | None = None
    name: str
    point: int
    default: bool
