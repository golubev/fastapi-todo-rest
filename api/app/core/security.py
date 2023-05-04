from datetime import datetime, timedelta
from typing import Self

from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app.config import config

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


class AccessTokenException(Exception):
    pass


class AccessTokenPayload(BaseModel):
    sub: str
    exp: datetime

    @classmethod
    def decode_from_access_token(cls, token: str) -> Self:
        try:
            payload = jwt.decode(
                token, config.SECURITY_SECRET_KEY, algorithms=[ALGORITHM]
            )
            return cls(**payload)
        except (jwt.JWTError, ValidationError):
            raise AccessTokenException()

    def encode_to_access_token(self) -> str:
        return jwt.encode(
            self.dict(), key=config.SECURITY_SECRET_KEY, algorithm=ALGORITHM
        )


def create_access_token(subject: int | str) -> str:
    expire = datetime.utcnow() + timedelta(
        seconds=config.SECURITY_ACCESS_TOKEN_EXPIRE_SECONDS
    )
    token_payload = AccessTokenPayload(sub=str(subject), exp=expire)
    return token_payload.encode_to_access_token()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return crypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return crypt_context.hash(password)
