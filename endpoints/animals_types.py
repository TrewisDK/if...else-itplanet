from fastapi import Response, Request, APIRouter
from models import Animal, AnimalType
from database import SessionLocal
from utils.validate_auth import validate_auth
import schemas

db = SessionLocal()
router = APIRouter()


@router.delete('/{typeId}', status_code=200)
@router.delete('/', status_code=400)
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


@router.get("/{typeId}", status_code=200)
@router.get("/", status_code=400)
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


@router.post("/", status_code=201)
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


@router.put('/{typeId}', status_code=200)
@router.put('/', status_code=400)
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