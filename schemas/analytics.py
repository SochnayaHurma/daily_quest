from pydantic import BaseModel, Field


class JobUserAnalytics(BaseModel):
    task_done: int
    task_not_done: int
    coin_accepted: int
    coin_could_be: int
    job_id: int | None = None
    job_name: str | None = None

    def __hash__(self):
        return hash((self.job_id, self.job_name))

    def __eq__(self, other):
        return self.job_id == other.job_id and self.job_name == other.job_name


class TaskUserAnalytics(BaseModel):
    jobs: set[JobUserAnalytics] = Field(default_factory=set)
    task_done: int = 0
    task_not_done: int = 0
    coin_accepted: int = 0
    coin_could_be: int = 0

