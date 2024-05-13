from pydantic import BaseModel, Field

from schemas.contract import PublicContractDetail


class SimplePublicJob(BaseModel):
    id: int
    name: str
    default: bool


class UserJobRelation(BaseModel):
    user_id: int
    username: str
    jobs: list[SimplePublicJob] = Field(default_factory=list)


class PublicUserContractJobs(BaseModel):
    contract: PublicContractDetail
    user_relations: dict[int, UserJobRelation]
    no_relations: list[SimplePublicJob]


class PublicContractJobs(BaseModel):
    contract: PublicContractDetail
    contract_relations: list[SimplePublicJob] = Field(default_factory=list)
    no_relations: list[SimplePublicJob] = Field(default_factory=list)


class AddContractJob(BaseModel):
    contract_id: int
    job_id: int
    user_id: int | None = None


class DropContractJob(BaseModel):
    contract_id: int
    job_id: int


class AddUserToContractJob(BaseModel):
    contract_id: int
    job_id: int
    user_id: int | None = None
