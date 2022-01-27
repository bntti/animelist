import random
import string
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash


def generate_salt(length: int) -> str:
    symbols = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(symbols) for _ in range(length))


def hash_password(password: str, salt: str) -> str:
    password += salt
    password += getenv("PEPPER")
    return generate_password_hash(password)


def check_password(password: str, salt: str, password_hash: str) -> bool:
    password += salt
    password += getenv("PEPPER")
    return check_password_hash(password_hash, password)
