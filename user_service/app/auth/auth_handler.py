# This file is responsible for signing , encoding , decoding and returning JWTS
import time
from typing import Dict
import jwt
from decouple import config


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def signJWT(user_id: str) -> Dict[str, str]:
        payload = {
                "user_id": user_id,
                "expires": time.time() + 7200
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token


def decodeJWT(token: str) -> dict:
        try:
                decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                return decoded_token if decoded_token["expires"] >= time.time() else None
        except:
                return {}
