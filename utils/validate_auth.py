import base64

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from database import SessionLocal
from models import User

db = SessionLocal()


def validate_auth(header, return_email=False):
    try:
        if header.startswith('Basic '):
            data = header.split(" ")[1]
            data = base64.b64decode(data).decode('utf-8').split(":")
            user = db.query(User).filter(User.email == data[0])[0]
            ph = PasswordHasher()
            try:
                if ph.verify(user.hashed_password, data[1]):
                    if return_email:
                        return [True, data[0]]
                    else:
                        return True
            except VerifyMismatchError:
                return False
        else:
            return False

    except Exception as e:
        print(e)
        return False
