from fastapi import Response, Request, Path, APIRouter
from models import User
from sqlalchemy import and_
from database import SessionLocal
from utils.validate_auth import validate_auth

db = SessionLocal()
router = APIRouter()


@router.get("/search")
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


@router.get("/{id}", status_code=200)
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
