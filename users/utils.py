import bcrypt
import jwt
from django.conf import settings
from datetime import datetime, timedelta



def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_jwt(user_id: str) -> str:
    payload = {"user_id": str(user_id), "exp": datetime.utcnow() + timedelta(hours=1)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
