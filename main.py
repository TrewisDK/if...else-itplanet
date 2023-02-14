from typing import Union
from datetime import datetime

from fastapi import FastAPI, Body, Response, Request, Path
from models import User, AnimalType, Animal, LocationPoint, AnimalVisited
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from models import engine

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

app = FastAPI()


@app.get("/accounts/search")
def search_accounts(request: Request, response: Response):
    """get user account by id"""
    query_params = request.query_params
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

    query = db.query(User)
    filters = []
    if first_name is not None:
        filters.append(User.first_name.ilike(f"%{first_name}%"))
    if last_name is not None:
        filters.append(User.last_name.ilike(f"%{last_name}%"))
    if email is not None:
        filters.append(User.email.ilike(f"%{email}%"))
    result = query.filter(and_(*filters)).limit(size).offset(from_).all()

    for user in result:
        accounts_searched.append({"id": user.id,
                                  "firstName": user.first_name,
                                  "lastName": user.last_name,
                                  "email": user.email})

    return accounts_searched


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
        try:
            datetime.fromisoformat(startDateTime)
        except ValueError:
            response.status_code = 400
            return {"message": "startDateTime must be in ISO 8601 format"}
        for animal in search_data:
            if datetime.fromisoformat(startDateTime) >= animal.chippingDateTime:
                animals.append(animal)

    if endDateTime is None:
        pass
    else:
        try:
            datetime.fromisoformat(startDateTime)
        except ValueError:
            response.status_code = 400
            return {"message": "startDateTime must be in ISO 8601 format"}
        for animal in search_data:
            if datetime.fromisoformat(startDateTime) <= animal.chippingDateTime:
                animals.append(animal)

    if chipperId is None:
        pass
    else:
        for animal in search_data:
            if animal.chipperId == int(chipperId):
                animals.append(animal)
    return {"data": animals}


@app.get("/animals/{animalId}", status_code=200)
def get_animal(response: Response, animalId: int = Path()):
    """get animal by id"""
    if animalId is None or animalId <= 0:
        response.status_code = 400
        return {"message": "animalId cannot be less than 1"}
    #animal = db.get(Animal, animalId)
    animal = db.query(Animal,  AnimalVisited.id).join(AnimalVisited).filter(Animal.id == AnimalVisited.animal_id).all()

    #
    # if animal is None:
    #     response.status_code = 404
    #     return {"message": "animal not found"}
    # return {"id": animal.id,
    #         "animalTypes": animal.animalTypes,
    #         "weight": animal.weight, "length": animal.lenght, "height": animal.height,
    #         "gender": animal.gender, "lifeStatus": animal.lifeStatus, "chippingDateTime": animal.chippingDateTime,
    #         "chipperId": animal.chipperId, "chippingLocationId": animal.chippingLocationId,
    #         "visitedLocations": animal.visitedLocations_id, "deathDateTime": animal.deathDateTime}
