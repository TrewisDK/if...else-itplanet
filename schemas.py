from pydantic import BaseModel


class Account(BaseModel):
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    password: str | None = None


class Locations(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
