from typing import Union

from fastapi import FastAPI, Body, Response, Request, Path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY, BigInteger, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session

# Подключаемся к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root@127.0.0.1/itplanet"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Base = declarative_base()


# Модель пользователя


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Animal(Base):
    __tablename__ = "animals"

    id = Column(BigInteger, primary_key=True)
    animalTypes = Column(ARRAY(BigInteger))
    weight = Column(Float)
    lenght = Column(Float)
    height = Column(Float)
    gender = Column(String)
    lifeStatus = Column(String)
    chippingDateTime = Column(DateTime)
    chipperId = Column(Integer, ForeignKey(User.id))
    chippingLocationId = Column(BigInteger)
    visitedLocations = Column(ARRAY(BigInteger))
    deathDateTime = Column(DateTime)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

app = FastAPI()


@app.get("/accounts/search")
def search_accounts(request: Request, response: Response):
    """get user account by id"""
    query_params = request.query_params
    search_data = db.query(User).all()
    accounts_searched = []

    try:
        first_name = query_params["firstName"]
    except KeyError:
        first_name = None
    try:
        last_name = query_params["lastName"]
    except KeyError:
        last_name = None
    try:
        email = query_params["email"]
    except KeyError:
        email = None
    try:
        from_ = query_params["from"]
    except KeyError:
        from_ = 0
    try:
        size = query_params["size"]
    except KeyError:
        size = 10

    if int(from_) < 0 or int(size) < 1:
        response.status_code = 400
        return {"message": "bad request"}

    if first_name is None:
        pass
    else:
        for user in search_data:
            if first_name.lower() in user.first_name.lower():
                accounts_searched.append(user)
    if last_name is None:
        pass
    else:
        for user in search_data:
            if last_name.lower() in user.last_name.lower():
                accounts_searched.append(user)
    if email is None:
        pass
    else:
        for user in search_data:
            if email.lower() in user.email.lower():
                accounts_searched.append(user)

    accounts_searched = list(set(accounts_searched))
    accounts_searched.sort(key=lambda dictionary: dictionary.id)
    cleaned_data = []

    for user in accounts_searched:
        cleaned_data.append({"id": user.id,
                             "firstName": user.first_name,
                             "lastName": user.last_name,
                             "email": user.email})

    return cleaned_data


@app.get("/accounts/{id}", status_code=200)
def account_data(response: Response, id: int = Path()):
    """search user account"""
    if id < 1 or id is None:
        response.status_code = 400
        return {"message": "id cannot be less than 1"}

    account = db.get(User, id)

    if account is None:
        response.status_code = 404
        return {"message": "Not Found"}

    return {"id": account.id, "firsName": account.first_name, "lastName": account.last_name,
            "email": account.email}


@app.get("/animals/search")
def search_animals(request: Request, response: Response):
    query_params = request.query_params
    search_data = db.query(Animal).all()
    animals = []

    try:
        startDateTime = query_params["startDateTime"]
    except KeyError:
        startDateTime = None
    try:
        endDateTime = query_params["endDateTime"]
    except KeyError:
        endDateTime = None
    try:
        chipperId = query_params["chipperId"]
    except KeyError:
        chipperId = None
    try:
        chippingLocationId = query_params["chippingLocationId"]
    except KeyError:
        chippingLocationId = None
    try:
        lifeStatus = query_params["lifeStatus"]
    except KeyError:
        lifeStatus = None
    try:
        gender = query_params["gender"]
    except KeyError:
        gender = None
    try:
        from_ = query_params["from"]
    except KeyError:
        from_ = 0
    try:
        size = query_params["size"]
    except KeyError:
        size = 10

    if int(from_) < 0 or int(size) < 1:
        response.status_code = 400
        return {"message": "bad request"}

    if startDateTime is None:
        pass
    else:
        pass


@app.get("/animals/{animalId}", status_code=200)
def get_animal(response: Response, animalId: int = Path()):
    """get animal by id"""
    if animalId is None or animalId <= 0:
        response.status_code = 400
        return {"message": "animalId cannot be less than 1"}
    animal = db.get(Animal, animalId)
    if animal is None:
        response.status_code = 404
        return {"message": "animal not found"}
    return {"id": animal.id,
            "animalTypes": animal.animalTypes,
            "weight": animal.weight, "length": animal.lenght, "height": animal.height,
            "gender": animal.gender, "lifeStatus": animal.lifeStatus, "chippingDateTime": animal.chippingDateTime,
            "chipperId": animal.chipperId, "chippingLocationId": animal.chippingLocationId,
            "visitedLocations": animal.visitedLocations, "deathDateTime": animal.deathDateTime}