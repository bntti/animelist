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

    def get_user_id(self, username: str) -> int:
        username = username.lower()
        sql = "SELECT id FROM users WHERE username = :username"
        result = self.database.session.execute(sql, {"username": username})
        return result.fetchone()[0]

    def add_user(self, username: str, password: str) -> int:
        username = username.lower()
        salt = generate_salt(16)
        password_hash = hash_password(password, salt)

        sql = "INSERT INTO users (username, salt, password) " \
              "VALUES (:username, :salt, :password) RETURNING id"
        result = self.database.session.execute(
            sql, {"username": username, "salt": salt, "password": password_hash}
        )
        self.commit()
        return result.fetchone()[0]

    def login(self, username: str, password: str) -> bool:
        username = username.lower()

        sql = "SELECT salt, password FROM users WHERE username = :username"
        result = self.database.session.execute(sql, {"username": username})
        salt, password_hash = result.fetchall()[0]

        return check_password(password, salt, password_hash)

    # Animes table
    def anime_count(self, query: str) -> int:
        if not query:
            sql = "SELECT COUNT(*) FROM animes WHERE NOT hidden"
        else:
            sql = "SELECT COUNT(*) FROM animes a, synonyms s " \
                  "WHERE NOT a.hidden AND a.id = s.anime_id AND " \
                  "(a.title ILIKE :query OR s.synonym ILIKE :query) GROUP BY a.id"
        result = self.database.session.execute(
            sql, {"query": f"%{query}%"}
        ).fetchone()
        return result[0] if result else 0

    def add_anime(self, anime: dict) -> int:
        sql = "INSERT INTO animes (title, episodes, link, picture, thumbnail, hidden) " \
              "VALUES (:title, :episodes, :link, :picture, :thumbnail, :hidden) " \
              "Returning id"
        return self.database.session.execute(sql, anime).fetchone()[0]

    def get_anime(self, anime_id: int) -> dict | None:
        sql = "SELECT title, episodes, picture FROM animes WHERE id = :id"
        result = self.database.session.execute(sql, {"id": anime_id})
        row = result.fetchone()
        if not row:
            return None
        return {
            "title": row[0],
            "episodes": row[1],
            "picture": row[2]
        }

    def get_animes(self, page: int, query: str) -> list:
        if not query:
            sql = "SELECT id, title, thumbnail FROM animes " \
                  "WHERE NOT hidden ORDER BY title LIMIT 50 OFFSET :offset"
        else:
            sql = "SELECT a.id, a.title, a.thumbnail FROM animes a, synonyms s " \
                "WHERE NOT a.hidden AND a.id = s.anime_id AND " \
                "(a.title ILIKE :query OR s.synonym ILIKE :query) " \
                "GROUP BY a.id ORDER BY title LIMIT 50 OFFSET :offset"
        result = self.database.session.execute(
            sql, {"offset": page, "query": f"%{query}%"}
        )

        return [{
                "id": row[0],
                "title": row[1],
                "thumbnail": row[2]
                } for row in result.fetchall()]

    # Tags table
    def add_tag(self, anime_id: int, tag: str) -> None:
        sql = "INSERT INTO tags (anime_id, tag) VALUES (:anime_id, :tag)"
        self.database.session.execute(sql, {"anime_id": anime_id, "tag": tag})

    # Synonyms table
    def add_synonym(self, anime_id: int, synonym: str) -> None:
        sql = "INSERT INTO synonyms (anime_id, synonym) VALUES (:anime_id, :synonym)"
        self.database.session.execute(
            sql, {"anime_id": anime_id, "synonym": synonym}
        )

    # List table
    def add_to_list(self, user_id: int, anime_id: int) -> None:
        try:
            sql = "INSERT INTO list (user_id, anime_id, episodes, status) " \
                "VALUES (:user_id, :anime_id, 0, 'WATCHING')"
            self.database.session.execute(
                sql, {"user_id": user_id, "anime_id": anime_id}
            )
            self.database.session.commit()
        except:
            # UNIQUE constraint fail
            self.database.session.rollback()

    def get_list_ids(self, user_id) -> list:
        sql = "SELECT  anime_id FROM list WHERE user_id = :user_id"
        result = self.database.session.execute(sql, {"user_id": user_id})
        return [row[0] for row in result.fetchall()]

    def get_list(self, user_id: int, ) -> list:
        sql = "SELECT  a.title, a.episodes, a.thumbnail, l.episodes, l.rating, l.status " \
              "FROM list l, animes a WHERE l.anime_id = a.id AND l.user_id = :user_id"
        result = self.database.session.execute(sql, {"user_id": user_id})

        return [{
                "title": row[0],
                "episodes": row[1],
                "thumbnail": row[2],
                "watched_episodes": row[3],
                "rating": row[4],
                "status": row[5]
                } for row in result.fetchall()]
