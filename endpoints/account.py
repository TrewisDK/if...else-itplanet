from fastapi import Response, Request, APIRouter
from validate_email import validate_email

import schemas
from models import User, Animal
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
@router.get("/", status_code=400)
def account_data(request: Request, response: Response, id: int = None):
    """search user account"""
    try:
        auth = request.headers["Authorization"]
        if validate_auth(auth) is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
    except KeyError:
        pass
    if id is None or id <= 0:
        response.status_code = 400
        return {"message": "Bad data"}

    account = db.get(User, id)

    if account is None:
        for i in range(1000):
            print("hello")
        response.status_code = 404
        return {"message": 1}
    return {"id": account.id, "firsName": account.first_name, "lastName": account.last_name,
            "email": account.email}


@router.put("/{id}", status_code=200)
@router.put("/", status_code=400)
def update_account_data(request: Request, response: Response, account: schemas.Account, id: int = None):
    account_update = db.get(User, id)
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if account_update is None or validate[1] != account_update.email:
            response.status_code = 403
            return {"message": "Bad account"}
        if id is None or id <= 0:
            response.status_code = 400
            return {"message": "Bad data"}
        if account.firstName is None or account.firstName == "" or account.firstName.isspace():
            response.status_code = 400
            return {"message": "Bad data"}
        if account.lastName is None or account.lastName == "" or account.lastName.isspace():
            response.status_code = 400
            return {"message": "Bad data"}
        if account.email is None or account.email == "" or account.email.isspace() or validate_email(
                account.email) is not True:
            response.status_code = 400
            return {"message": "Bad data"}
        if account.password is None or account.password == "" or account.password.isspace():
            response.status_code = 400
            return {"message": "Bad data"}
        user_account = db.query(User).filter_by(id=id).first()
        if len(db.query(User).filter_by(email=account.email).all()) > 0 and user_account.email != account.email:
            response.status_code = 409
            return {"message": "An account with this email already exists"}
        user_account.first_name = account.firstName
        user_account.last_name = account.lastName
        user_account.email = account.email
        db.commit()
        response.status_code = 200
        return {
            "id": id,
            "firstName": account.firstName,
            "lastName": account.lastName,
            "email": account.email
        }
    except (KeyError, TypeError):
        response.status_code = 401
        return {"message": "Invalid authorization data"}


@router.delete("/{id}", status_code=200)
@router.delete("/", status_code=400)
def delete_account(request: Request, response: Response, id: int = None):
    account_update = db.get(User, id)
    try:
        auth = request.headers["Authorization"]
        validate = validate_auth(auth, return_email=True)

        if validate[0] is not True:
            response.status_code = 401
            return {"message": "Invalid authorization data"}
        if account_update is None or validate[1] != account_update.email:
            response.status_code = 403
            return {"message": "Bad account"}
        if id is None or id <= 0 or len(db.query(Animal).filter_by(chipperId=id).all()) > 0:
            response.status_code = 400
            return {"message": "Bad data"}
        account = db.query(User).get(id)
        db.delete(account)
        db.commit()
        response.status_code = 200
        return {}
    except (KeyError, TypeError) as e:
        print(e)
        response.status_code = 401
        return {"message": "Invalid authorization data"}
