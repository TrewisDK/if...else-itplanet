from pydantic import BaseModel
from typing import List, Optional


class Account(BaseModel):
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    password: str | None = None


class Locations(BaseModel):
    latitude: float | None = None
    longitude: float | None = None


class AnimalType(BaseModel):
    type: str | None = None


class Animal(BaseModel):
    animalTypes: List[Optional[int]] | None = None
    weight: float | None = None
    length: float | None = None
    height: float | None = None
    gender: str | None = None
    chipperId: int | None = None
    chippingLocationId: int | None = None
    lifeStatus: str | None = None


class NewType(BaseModel):
    oldTypeId: int | None = None
    newTypeId: int | None = None
