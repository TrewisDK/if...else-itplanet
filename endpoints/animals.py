from fastapi import Response, Request, Path, APIRouter
from models import Animal, AnimalVisited, AnimalType, animal_types
from datetime import datetime
from sqlalchemy import and_, select
from database import SessionLocal
from utils.validate_auth import validate_auth
import schemas

db = SessionLocal()
router = APIRouter()


@router.get("/{animalId}/locations", status_code=200)
def get_visited_locations(request: Request, response: Response, animalId: int = None):
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

    if animalId is None or animalId <= 0:
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


@router.get("/search")
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


@router.get("/{animalId}", status_code=200)
@router.get("/", status_code=400)
def get_animal(request: Request, response: Response, animalId: int = None):
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


@router.get("/types/{typeId}", status_code=200)
@router.get("/types/", status_code=400)
def get_animal_type(request: Request, response: Response, typeId: int = None):
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


@router.post("/types", status_code=201)
def add_animal_type(request: Request, response: Response, animalType: schemas.AnimalType):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if animalType.type is None or animalType.type == "" or animalType.type.isspace():
            response.status_code = 400
            return {"message": "Bad data"}
        if len(db.query(AnimalType).filter_by(animaltype=animalType.type).all()) > 0:
            response.status_code = 409
            return {"message": "This type already exists "}
        new_animal_type = AnimalType(
            animaltype=animalType.type
        )
        db.add(new_animal_type)
        db.commit()
        return {
            "id": new_animal_type.id,
            "type": new_animal_type.animaltype
        }

    except (KeyError, TypeError):
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.put('/types/{typeId}', status_code=200)
@router.put('/types/', status_code=400)
def change_type(request: Request, response: Response, animalType: schemas.AnimalType, typeId: int = None):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if typeId is None or typeId <= 0 or animalType.type is None or animalType.type == "" or animalType.type.isspace():
            response.status_code = 400
            return {"message": "Bad data"}
        if len(db.query(AnimalType).filter_by(animaltype=animalType.type).all()) > 0:
            response.status_code = 409
            return {"message": "This type already exists "}
        animalTypeNow = db.query(AnimalType).get(typeId)
        if animalTypeNow is None:
            response.status_code = 404
            return {"message": "Not Found"}
        animalTypeNow.animaltype = animalType.type
        db.commit()
        return {
            "id": animalTypeNow.id,
            "type": animalTypeNow.animaltype
        }

    except (KeyError, TypeError):
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.delete('/types/{typeId}', status_code=200)
@router.delete('/types/', status_code=400)
def delete_animal_type(request: Request, response: Response, typeId: int = None):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        animalType = db.query(AnimalType).get(typeId)
        if animalType is None:
            response.status_code = 404
            return {"message": "Not Found"}
        if typeId is None or typeId <= 0 or len(db.query(Animal).join(Animal.animalTypes).filter(AnimalType.id == typeId).all()):
            response.status_code = 400
            return {"message": "Bad data"}

        db.delete(animalType)
        db.commit()
        return {}

    except (KeyError, TypeError):
        response.status_code = 401
        return {"message": "Invalid authorization data"}
