from fastapi import Response, Request, Path, APIRouter
from models import LocationPoint, Animal, AnimalVisited
from database import SessionLocal
from utils.validate_auth import validate_auth
import schemas
from pydantic import BaseModel

db = SessionLocal()
router = APIRouter()


@router.post("/", status_code=201)
def add_location(request: Request, response: Response, new_location: schemas.Locations):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if new_location.latitude is None or new_location.latitude < -90 or new_location.latitude > 90:
            response.status_code = 400
            return {"message": "bad latitude"}
        if new_location.longitude is None or new_location.longitude < -180 or new_location.longitude > 180:
            response.status_code = 400
            return {"message": "bad longitude"}
        if len(db.query(LocationPoint).filter_by(latitude=new_location.latitude,
                                                 longitude=new_location.longitude).all()) > 0:
            response.status_code = 409
            return {"message": "Location with this latitude already exists"}
        created_location = LocationPoint(
            latitude=new_location.latitude,
            longitude=new_location.longitude
        )
        db.add(created_location)
        db.commit()
        return {
            "id": created_location.id,
            "latitude": created_location.latitude,
            "longitude": created_location.longitude
        }
    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.get("/{pointId}", status_code=200)
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


@router.put("/{pointId}", status_code=200)
def change_location(request: Request, response: Response, new_location: schemas.Locations, pointId: int = Path()):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if pointId is None or pointId <= 0:
            response.status_code = 400
            return {"message": "bad pointId"}
        if new_location.latitude is None or new_location.latitude < -90 or new_location.latitude > 90:
            response.status_code = 400
            return {"message": "bad latitude"}
        if new_location.longitude is None or new_location.longitude < -180 or new_location.longitude > 180:
            response.status_code = 400
            return {"message": "bad longitude"}
        if len(db.query(LocationPoint).filter_by(latitude=new_location.latitude,
                                                 longitude=new_location.longitude).all()) > 0:
            response.status_code = 409
            return {"message": "Location with this latitude already exists"}
        location = db.query(LocationPoint).get(pointId)
        if location is None:
            response.status_code = 404
            return {"message": "Location not found"}
        location.latitude = new_location.latitude
        location.longitude = new_location.longitude
        db.commit()
        return {
            "id": location.id,
            "latitude": location.latitude,
            "longitude": location.longitude
        }
    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.delete("/{pointId}", status_code=200)
def delete_location(request: Request, response: Response, pointId: int = Path()):
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if pointId is None or pointId <= 0 or len(
                db.query(Animal).filter_by(chippingLocationId=pointId).all()) > 0 or len(
                db.query(AnimalVisited).filter_by(location=pointId).all()) > 0:
            response.status_code = 400
            return {"message": "bad data"}
        location = db.query(LocationPoint).get(pointId)
        if location is None:
            response.status_code = 404
            return {"message": "Location not found"}
        db.delete(location)
        db.commit()
        return {}


    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}
