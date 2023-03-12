from fastapi import Response, Request, APIRouter
from models import Animal, AnimalVisited, User, LocationPoint, AnimalType, animal_types
from datetime import datetime
from sqlalchemy import and_
from database import SessionLocal
from utils.validate_auth import validate_auth
import schemas

db = SessionLocal()
router = APIRouter()


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


@router.post("/", status_code=201)
def create_new_animal(request: Request, response: Response, animal: schemas.Animal):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if animal.animalTypes is None or len(animal.animalTypes) <= 0 or None in animal.animalTypes or any(
                i <= 0 for i in animal.animalTypes) \
                or animal.weight is None or animal.weight <= 0 \
                or animal.length is None or animal.length <= 0 \
                or animal.height is None or animal.height <= 0 \
                or animal.gender is None or animal.gender != "MALE" and animal.gender != "FEMALE" and animal.gender != "OTHER" \
                or animal.chipperId is None or animal.chipperId <= 0 \
                or animal.chippingLocationId is None or animal.chippingLocationId <= 0:
            response.status_code = 400
            return {"message": "Bad data"}
        if db.query(User).get(animal.chipperId) is None or db.query(LocationPoint).get(
                animal.chippingLocationId) is None or len(
            db.query(AnimalType).filter(AnimalType.id.in_(animal.animalTypes)).all()) != len(animal.animalTypes):
            response.status_code = 404
            return {"message": "Not Found"}
        if list(set(animal.animalTypes)) != animal.animalTypes:
            response.status_code = 409
            return {"message": "Conflict"}
        new_animal = Animal(
            weight=animal.weight,
            lenght=animal.length,
            height=animal.height,
            gender=animal.gender,
            lifeStatus="ALIVE",
            chippingDateTime=datetime.now().isoformat(),
            chipperId=animal.chipperId,
            visitedLocations=[],
            chippingLocationId=animal.chippingLocationId,
            deathDateTime=None
        )
        db.add(new_animal)
        db.commit()
        for typeid in animal.animalTypes:
            add_type = animal_types.insert().values(animal_id=new_animal.id, animal_type_id=typeid)
            db.execute(add_type)
            db.commit()
        return {
            "id": new_animal.id,
            "animalTypes": [type_id.id for type_id in new_animal.animalTypes],
            "weight": new_animal.weight,
            "length": new_animal.lenght,
            "height": new_animal.height,
            "gender": new_animal.gender,
            "lifeStatus": new_animal.lifeStatus,
            "chippingDateTime": new_animal.chippingDateTime,
            "chipperId": new_animal.chipperId,
            "chippingLocationId": new_animal.chippingLocationId,
            "visitedLocations": [location.id for location in new_animal.visitedLocations],
            "deathDateTime": new_animal.deathDateTime
        }

    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.put("/{animalId}", status_code=200)
@router.put("/", status_code=200)
def change_animal(request: Request, response: Response, animal: schemas.Animal, animalId: int = None):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if animalId is None or animalId <= 1 \
                or animal.weight is None or animal.weight <= 0 \
                or animal.length is None or animal.length <= 0 \
                or animal.height is None or animal.height <= 0 \
                or animal.gender != "MALE" and animal.gender != "FEMALE" and animal.gender != "OTHER" \
                or animal.lifeStatus != "DEAD" and animal.lifeStatus != "ALIVE" \
                or animal.chipperId is None or animal.chipperId <= 0 \
                or animal.chippingLocationId is None or animal.chippingLocationId <= 0:
            response.status_code = 400
            return {"message": "Bad data"}
        animal_for_update = db.query(Animal).get(animalId)
        if animal_for_update is None or db.query(User).get(animal.chipperId) is None or db.query(LocationPoint).get(
                animal.chippingLocationId) is None:
            response.status_code = 404
            return {"message": "Not Found"}
        if animal_for_update.lifeStatus == "DEAD" and animal.lifeStatus == "ALIVE" \
                or len([location.id for location in animal_for_update.visitedLocations]) < 0 and \
                [location.id for location in animal_for_update.visitedLocations][0] == animal.chippingLocationId:
            response.status_code = 400
            return {"message": "Bad data"}
        if animal.lifeStatus == "DEAD":
            animal_for_update.deathDateTime = datetime.now().isoformat()
            db.commit()
        animal_for_update.weight = animal.weight
        animal_for_update.length = animal.length
        animal_for_update.height = animal.height
        animal_for_update.gender = animal.gender
        animal_for_update.lifeStatus = animal.lifeStatus
        animal_for_update.chipperId = animal.chipperId
        animal_for_update.chippingLocationId = animal.chippingLocationId
        db.commit()
        return {
            "id": animal_for_update.id,
            "animalTypes": [type_id.id for type_id in animal_for_update.animalTypes],
            "weight": animal_for_update.weight,
            "length": animal_for_update.lenght,
            "height": animal_for_update.height,
            "gender": animal_for_update.gender,
            "lifeStatus": animal_for_update.lifeStatus,
            "chippingDateTime": animal_for_update.chippingDateTime,
            "chipperId": animal_for_update.chipperId,
            "chippingLocationId": animal_for_update.chippingLocationId,
            "visitedLocations": [location.id for location in animal_for_update.visitedLocations],
            "deathDateTime": animal_for_update.deathDateTime
        }
    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.delete("/{animalId}", status_code=200)
@router.delete("/", status_code=400)
def delete_animal(request: Request, response: Response, animalId: int = None):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        animal = db.query(Animal).get(animalId)
        if animal is None:
            response.status_code = 404
            return {"message": "Not Found"}
        if animalId is None or animalId <= 0 or len(animal.visitedLocations) > 0:
            response.status_code = 400
            return {"message": "Bad data"}
        db.delete(animal)
        db.commit()
        return {}
    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}