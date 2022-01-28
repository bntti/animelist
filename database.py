from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from password import generate_salt, hash_password, check_password


class DB:
    def __init__(self, app: Flask) -> None:
        app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
        self.database = SQLAlchemy(app)

    def commit(self) -> None:
        self.database.session.commit()

    # Users table
    def user_exists(self, username: str) -> bool:
        username = username.lower()

        sql = "SELECT COUNT(*) FROM users WHERE username = :username"
        result = self.database.session.execute(sql, {"username": username})

        return result.fetchone()[0] > 0

    def add_user(self, username: str, password: str) -> None:
        username = username.lower()
        salt = generate_salt(16)
        password_hash = hash_password(password, salt)

        sql = "INSERT INTO users (username, salt, password) " \
              "VALUES (:username, :salt, :password)"
        self.database.session.execute(
            sql, {"username": username, "salt": salt, "password": password_hash}
        )
        self.commit()

    def login(self, username: str, password: str) -> bool:
        username = username.lower()

        sql = "SELECT salt, password " \
              "FROM users WHERE username = :username"
        result = self.database.session.execute(
            sql, {"username": username}
        )
        salt, password_hash = result.fetchall()[0]

        return check_password(password, salt, password_hash)

    # Animes table
    def anime_count(self) -> int:
        sql = "SELECT COUNT(*) FROM animes"
        return self.database.session.execute(sql).fetchone()[0]

    def add_anime(self, anime: dict) -> int:
        sql = "INSERT INTO animes (title, episodes, link, picture, thumbnail, hidden) " \
              "VALUES (:title, :episodes, :link, :picture, :thumbnail, :hidden) " \
              "Returning id"
        return self.database.session.execute(sql, anime).fetchone()[0]

    def get_anime(self, id: int) -> dict:
        sql = "SELECT title, episodes, picture FROM animes "\
              "WHERE id = :id"
        result = self.database.session.execute(sql, {"id": id})
        row = result.fetchone()
        if not row:
            return None
        return {
            "title": row[0],
            "episodes": row[1],
            "picture": row[2]
        }

    def get_animes(self, page: int) -> None:
        sql = "SELECT id, title, thumbnail FROM animes " \
              "WHERE NOT hidden " \
              "ORDER BY title LIMIT 50 OFFSET :offset"
        result = self.database.session.execute(sql, {"offset": page})
        animes = []
        for row in result.fetchall():
            animes.append({
                "id": row[0],
                "title": row[1],
                "thumbnail": row[2]
            })
        return animes

    # Tags table
    def add_tag(self, anime_id: int, tag: str) -> None:
        sql = "INSERT INTO tags (anime_id, tag) VALUES (:anime_id, :tag) "
        self.database.session.execute(sql, {"anime_id": anime_id, "tag": tag})
