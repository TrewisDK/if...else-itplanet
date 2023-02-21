from argon2 import PasswordHasher
from fastapi import Response, Request, APIRouter

import schemas
from models import User
from database import SessionLocal
from validate_email import validate_email

db = SessionLocal()
router = APIRouter()


@router.post("/", status_code=201)
def registration(request: Request, response: Response, account: schemas.Account):
    """registration account"""
    try:
        auth = request.headers["Authorization"]
        print(auth)
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
