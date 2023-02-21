from pydantic import BaseModel


class Account(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str
