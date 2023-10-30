from pydantic import BaseModel, Field, EmailStr, validator, model_validator, SecretStr
from typing import Optional, Any
from datetime import datetime
from uuid import UUID, uuid4
from database import DBClient, DBName, UserCollection, Collection
# from
import re


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
    username: str | None
    phoneno: str | None
    email: EmailStr | None
    password: str = Field(min_length=8, max_length=25)
    age: None | int = Field(gt=17, lt=101)
    Additional: dict

    @model_validator(mode='before')
    @classmethod
    def validating_username_phoneno_email(cls, field_values:Any):
        print(field_values)
        if field_values['username'] or field_values['phoneno'] or field_values['email']:
            if not list(DBClient[DBName][UserCollection].find({'$or': [{'username': field_values['username']},
                                                                       {'phoneno': field_values['phoneno']},
                                                                       {'email': field_values['email']}]})):
                return field_values
            raise ValueError("Already user exists with his details")
        else:
            raise ValueError("Provide valid information for username, phoneno, email")

    # @validator('email')
    # def email_Valitor(cls, value):
    #     regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    #     if value:
    #         if not re.fullmatch(regex, value):
    #             raise ValueError("Please provide valid Email")
    #     return value


class User(UserCreate):
    id: UUID = Field(default_factory=uuid4)
