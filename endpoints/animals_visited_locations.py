from fastapi import Response, Request, APIRouter
from models import Animal, AnimalVisited
from datetime import datetime
from sqlalchemy import and_
from database import SessionLocal
from utils.validate_auth import validate_auth
import schemas

db = SessionLocal()
router = APIRouter()


@router.get("/", status_code=200)
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
