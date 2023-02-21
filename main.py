from typing import Union
from datetime import datetime

from argon2.exceptions import VerifyMismatchError
from validate_email import validate_email
from argon2 import PasswordHasher
import base64

from fastapi import FastAPI, Response, Request, Path
from models import User, AnimalType, Animal, LocationPoint, AnimalVisited
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from models import engine
import pydanticmodels

SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()

app = FastAPI()


def validate_auth(header):
    try:
        if header.startswith('Basic '):
            data = header.split(" ")[1]
            data = base64.b64decode(data).decode('utf-8').split(":")
            user = db.query(User).filter(User.email == data[0])[0]
            ph = PasswordHasher()
            try:
                if ph.verify(user.hashed_password, data[1]):
                    return True
            except VerifyMismatchError:
                return False
        else:
            return False

    except Exception as e:
        print(e)
        return False


@app.get("/accounts/search")
def search_accounts(request: Request, response: Response):
    """get user account by id"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
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
def account_data(request: Request, response: Response, id: int = Path()):
    """search user account"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    if id < 1 or id is None:
        response.status_code = 400
        return {"message": "id cannot be less than 1"}

    account = db.get(User, id)

    if account is None:
        response.status_code = 404
        return {"message": "Not Found"}

    return {"id": account.id, "firsName": account.first_name, "lastName": account.last_name,
            "email": account.email}


@app.get("/animals/{animalId}/locations", status_code=200)
def get_visited_locations(request: Request, response: Response, animalId: int = Path()):
    """pass"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    query_params = request.query_params
    filtered_locations = []

    try:
        startDateTime = query_params["startDateTime"]
    except KeyError:
        startDateTime = None
    try:
        endDateTime = query_params['endDateTime']
    except KeyError:
        endDateTime = None
    try:
        from_ = query_params["from"]
    except KeyError:
        from_ = 0
    try:
        size = query_params["size"]
    except KeyError:
        size = 10

    if int(from_) < 0 or int(size) <= 0:
        response.status_code = 400
        return {"message": "bad request"}

    if animalId <= 0 or animalId is None:
        response.status_code = 400
        return {"message": "bad request"}

    animal = db.get(Animal, animalId)
    if animal is None:
        response.status_code = 404
        return {"message": "animal not found"}
    locations = db.query(AnimalVisited)
    filters = []
    filters.append(AnimalVisited.animal_id == animalId)
    if startDateTime is not None:
        try:
            filters.append(AnimalVisited.datetime_of_visited_location >= datetime.fromisoformat(startDateTime))
        except ValueError:
            response.status_code = 400
            return {"message": "startDateTime must be in ISO 8601 format"}
    if endDateTime is not None:
        try:
            filters.append(AnimalVisited.datetime_of_visited_location <= datetime.fromisoformat(endDateTime))
        except ValueError:
            response.status_code = 400
            return {"message": "endDateTime must be in ISO 8601 format"}
    result = locations.filter(and_(*filters)).limit(size).offset(from_).all()
    for location in result:
        filtered_locations.append({
            "id": location.id,
            "dateTimeOfVisitLocationPoint": location.datetime_of_visited_location,
            "locationPointId": location.location
        })
    return filtered_locations


@app.get("/animals/search")
def search_animals(request: Request, response: Response):
    """pass"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    query_params = request.query_params

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

    if int(from_) < 0 or int(size) <= 0:
        response.status_code = 400
        return {"message": "bad request"}

    query = db.query(Animal)
    filters = []
    animals_searched = []
    if startDateTime is not None:
        try:
            filters.append(Animal.chippingDateTime >= datetime.fromisoformat(startDateTime))
        except ValueError:
            response.status_code = 400
            return {"message": "startDateTime must be in ISO 8601 format"}
    if endDateTime is not None:
        try:
            filters.append(Animal.chippingDateTime <= datetime.fromisoformat(endDateTime))
        except ValueError:
            response.status_code = 400
            return {"message": "endDateTime must be in ISO 8601 format"}
    if chipperId is not None:
        if chipperId <= 0:
            response.status_code = 400
            return {"message": "chipperId must be >0 "}
        else:
            filters.append(Animal.chipperId == int(chipperId))
    if chippingLocationId is not None:
        if chippingLocationId <= 0:
            response.status_code = 400
            return {"message": "chippingLocationId must be > 0"}
        filters.append(Animal.chippingLocationId == int(chippingLocationId))
    if lifeStatus is not None:
        if lifeStatus != "ALIVE" and lifeStatus != "DEAD":
            response.status_code = 400
            return {"message": "lifeStatus must be 'ALIVE' or 'DEAD'"}
        else:
            filters.append(Animal.lifeStatus == lifeStatus)
    if gender is not None:
        if gender != "MALE" and gender != "FEMALE" and gender != "OTHER":
            response.status_code = 400
            return {"message": "gender must be 'MALE' or 'FEMALE' or 'OTHER'"}
        else:
            filters.append(Animal.gender == gender)

    result = query.filter(and_(*filters)).limit(size).offset(from_).all()

    for animal in result:
        animals_searched.append({
            'id': animal.id,
            'animalTypes': [type_id.id for type_id in animal.animalTypes],
            'weight': animal.weight,
            'length': animal.lenght,
            'height': animal.height,
            'gender': animal.gender,
            'lifeStatus': animal.lifeStatus,
            'chippingDateTime': animal.chippingDateTime,
            'chipperId': animal.chipperId,
            'chippingLocationId': animal.chippingLocationId,
            'visitedLocations': [location.id for location in animal.visitedLocations],
            'deathDateTime': animal.deathDateTime
        })
    return animals_searched


@app.get("/animals/{animalId}", status_code=200)
def get_animal(request: Request, response: Response, animalId: int = Path()):
    """get animal by id"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    if animalId is None or animalId <= 0:
        response.status_code = 400
        return {"message": "animalId cannot be less than 1"}
    animal = db.get(Animal, animalId)
    if animal is None:
        response.status_code = 404
        return {"message": "animal not found"}

    return {"id": animal.id,
            "animalTypes": [type_id.id for type_id in animal.animalTypes],
            "weight": animal.weight, "length": animal.lenght, "height": animal.height,
            "gender": animal.gender, "lifeStatus": animal.lifeStatus, "chippingDateTime": animal.chippingDateTime,
            "chipperId": animal.chipperId, "chippingLocationId": animal.chippingLocationId,
            "visitedLocations": [location.id for location in animal.visitedLocations],
            "deathDateTime": animal.deathDateTime}


@app.get("/animals/types/{typeId}", status_code=200)
def get_animal_type(request: Request, response: Response, typeId: int = Path()):
    """get animal type by id"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    if typeId is None or typeId <= 0:
        response.status_code = 400
        return {"message": "bad data"}
    animal_type = db.get(AnimalType, typeId)
    if animal_type is None:
        response.status_code = 404
        return {"message": "animal type not found"}

    return {
        "id": animal_type.id,
        "type": animal_type.animaltype
    }


@app.get("/locations/{pointId}", status_code=200)
def get_location(request: Request, response: Response, pointId: int = Path()):
    """get location by id"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    if pointId is None or pointId <= 0:
        response.status_code = 400
        return {"message": "bad data"}
    location = db.get(LocationPoint, pointId)
    if location is None:
        response.status_code = 404
        return {"message": "location not found"}

    return {
        "id": location.id,
        "latitude": location.latitude,
        "longitude": location.longitude
    }


@app.post("/registration", status_code=201)
def registration(request: Request, response: Response, account: pydanticmodels.Account):
    """registration account"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    try:
        auth = request.headers["Authorization"]
        response.status_code = 403
        return {"message": "auth user"}
    except KeyError:
        pass
    if account.firstName is None or account.firstName == "" or account.firstName.isspace():
        response.status_code = 400
        return {"message": "bad request"}
    if account.lastName is None or account.lastName == "" or account.lastName.isspace():
        response.status_code = 400
        return {"message": "bad request"}
    if account.email is None or account.email == "" or account.email.isspace() or validate_email(
            account.email) == False:
        response.status_code = 400
        return {"message": "bad request"}
    if account.password is None or account.password == "" or account.password.isspace():
        response.status_code = 400
        return {"message": "bad request"}
    if len(db.query(User).filter(User.email == account.email).all()) > 0:
        response.status_code = 409
        return {"message": "an account with this email already exists"}
    ph = PasswordHasher()
    hashed_password = ph.hash(account.password)
    new_account = User(
        first_name=account.firstName,
        last_name=account.lastName,
        email=account.email,
        hashed_password=hashed_password
    )
    db.add(new_account)
    db.commit()

    return {
        "id": new_account.id,
        "firstName": new_account.first_name,
        "lastName": new_account.last_name,
        "email": new_account.email
    }
