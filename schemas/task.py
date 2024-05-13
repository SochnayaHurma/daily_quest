from typing import Optional

from pydantic import BaseModel

from schemas import PublicJob


class ToggleTaskStatus(BaseModel):
    task_id: int
    done: bool


class ToggleTaskJob(BaseModel):
    task_id: int
    job_id: int | None = None


class PublicTask(BaseModel):
    id: int | None = None
    job: Optional[PublicJob] = None
    done: bool = False
    contract_id: int
