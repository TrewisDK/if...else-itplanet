from fastapi import Response, Request, Path, APIRouter
from models import LocationPoint
from database import SessionLocal
from utils.validate_auth import validate_auth

db = SessionLocal()
router = APIRouter()


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
