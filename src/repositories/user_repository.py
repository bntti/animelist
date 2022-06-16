from typing import Optional

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from database import database


def check_password(username: str, password: str) -> bool:
    sql = "SELECT password FROM users WHERE username = :username"
    result = database.session.execute(sql, {"username": username})
    password_hash = result.fetchone()[0]
    return check_password_hash(password_hash, password)


def username_taken(username: str) -> bool:
    sql = "SELECT COUNT(*) FROM users WHERE LOWER(username) = LOWER(:username)"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()[0] > 0


def username_exists(username: str) -> bool:
    sql = "SELECT COUNT(*) FROM users WHERE username = :username"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()[0] > 0


def get_user_data(username: str) -> Optional[tuple[int, bool]]:
    sql = "SELECT id, show_hidden FROM users WHERE username = :username"
    result = database.session.execute(sql, {"username": username})
    return result.fetchone()


def set_show_hidden(new_show_hidden: bool) -> None:
    sql = "UPDATE users SET show_hidden = :show_hidden WHERE id = :user_id"
    database.session.execute(
        sql, {"user_id": session["user_id"], "show_hidden": new_show_hidden}
    )
    database.session.commit()


def add_user(username: str, password: str) -> int:
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id"
    result = database.session.execute(
        sql, {"username": username, "password": password_hash}
    )
    database.session.commit()
    return result.fetchone()[0]
