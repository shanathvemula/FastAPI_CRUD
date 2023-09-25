from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Blog(BaseModel):
    # id: UUID = Field(default_factory=uuid4)
    id: int
    title: str
    blog: str
    author: str = Field(max_length=10, min_length=5)
    pages: int = Field(ge=12, le=100)
    published_at: Optional[datetime]
    published: Optional[bool]
    Additional: list | dict | None

    class Config:
        json_schema_extra = {
            'example': {
                "_id": 1,
                "title": "Title",
                "blog": "This is the test blog",
                "author": "Test",
                "pages": 0,
                "published_at": None,
                "published": False,
                "Additional": []
            }
        }


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=25)
    age: int = Field(gt=17, lt=101)

class User(UserCreate):
    id: UUID = Field(default_factory=uuid4)
