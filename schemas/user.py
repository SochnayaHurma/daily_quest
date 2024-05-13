from typing import Optional

from pydantic import BaseModel, Field


class PublicUser(BaseModel):
    id: Optional[int] = None
    username: str
    email: str


class CreateUserSchema(BaseModel):
    email: str = Field(min_length=4, max_length=60)
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=6, max_length=40)


class LoginUser(BaseModel):
    username: str
    password: str
