"""Autenticação: hash Argon2 + sessão JWT em cookie HttpOnly (RNF01)."""
import sys
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from app import config

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_token(username: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.TOKEN_MINUTES)
    return jwt.encode({"sub": username, "exp": exp}, config.SECRET_KEY, algorithm="HS256")


def read_token(token: str | None) -> str | None:
    if not token:
        return None
    try:
        return jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:
        return None


if __name__ == "__main__":
    # python -m app.security "minha-senha"
    print(hash_password(sys.argv[1]))
