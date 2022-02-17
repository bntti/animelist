from typing import Optional
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from defusedxml.ElementTree import fromstring, ParseError
from werkzeug.datastructures import FileStorage
from flask import session
from database import database


# Helper functions
def import_from_myanimelist(file: FileStorage) -> bool:
    try:
        root = fromstring(file.read())
    except ParseError:
        return False

    for anime_data in root:
        if anime_data.tag == "anime":
            anime = {
                "id": anime_data.find("./series_animedb_id").text,
                "episodes": int(anime_data.find("./my_watched_episodes").text),
                "score": anime_data.find("./my_score").text,
                "status": anime_data.find("./my_status").text,
                "times_watched": int(anime_data.find("./my_times_watched").text)
            }
            if anime["status"] == "Completed":
                anime["times_watched"] += 1
            import_to_list(session["user_id"], anime)

    return True


# Database functions
def add_to_list(user_id: int, anime_id: int) -> None:
    try:
        sql = "INSERT INTO list (user_id, anime_id) VALUES (:user_id, :anime_id)"
        database.session.execute(
            sql, {"user_id": user_id, "anime_id": anime_id}
        )
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def import_to_list(user_id, anime: dict):
    sql = "SELECT id FROM animes WHERE link = :link"
    result = database.session.execute(
        sql, {"link": f"https://myanimelist.net/anime/{anime['id']}"}
    ).fetchone()

    if not result:
        return

    anime_id = result[0]
    data = {**anime, "user_id": user_id, "anime_id": anime_id}

    try:
        sql = "INSERT INTO list (user_id, anime_id, episodes, score, status, times_watched) " \
              "VALUES (:user_id, :anime_id, :episodes, :score, :status, :times_watched)"
        database.session.execute(sql, data)
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def remove_from_list(user_id: int, anime_id: int) -> None:
    sql = "DELETE FROM list WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id}
    )
    database.session.commit()


def set_score(user_id: int, anime_id: int, score: Optional[int]) -> None:
    sql = "UPDATE list SET score = :score WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id, "score": score}
    )
    database.session.commit()


def set_times_watched(user_id: int, anime_id: int, times_watched: int) -> None:
    sql = "UPDATE list SET times_watched = :times_watched " \
          "WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql,
        {"user_id": user_id, "anime_id": anime_id, "times_watched": times_watched}
    )
    database.session.commit()


def add_times_watched(user_id: int, anime_id: int, add: int) -> None:
    sql = "UPDATE list SET times_watched = times_watched + :add " \
          "WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql,
        {"user_id": user_id, "anime_id": anime_id, "add": add}
    )
    database.session.commit()


def set_status(user_id: int, anime_id: int, status: str) -> None:
    sql = "UPDATE list SET status = :status WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql,
        {"user_id": user_id, "anime_id": anime_id, "status": status}
    )
    database.session.commit()


def set_episodes_watched(user_id: int, anime_id: int, episodes_watched: int) -> None:
    sql = "UPDATE list SET episodes = :episodes_watched " \
          "WHERE user_id = :user_id AND anime_id = :anime_id"

    database.session.execute(
        sql,
        {
            "user_id": user_id,
            "anime_id": anime_id,
            "episodes_watched": episodes_watched
        }
    )
    database.session.commit()


def get_user_anime_data(user_id: int, anime_id: int) -> Optional[dict]:
    sql = "SELECT score, episodes, status, times_watched FROM list " \
          "WHERE user_id = :user_id AND anime_id = :anime_id"
    row = database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id}
    ).fetchone()

    return None if not row else {
        "score": row[0],
        "episodes": row[1],
        "status": row[2],
        "times_watched": row[3],
        "in_list": True
    }


def get_list_ids(user_id) -> list:
    sql = "SELECT anime_id FROM list WHERE user_id = :user_id"
    result = database.session.execute(sql, {"user_id": user_id})
    return [row[0] for row in result.fetchall()]


def get_list_data(user_id: int, status: str) -> list:
    sql = "SELECT a.id, a.title, a.episodes, a.thumbnail, l.episodes, l.score " \
          "FROM list l, animes a WHERE l.anime_id = a.id AND l.user_id = :user_id " \
          "AND (l.status = :status OR :status = 'All') ORDER BY a.title"

    result = database.session.execute(
        sql, {"user_id": user_id, "status": status}
    )

    return [{
        "id": row[0],
        "title": row[1],
        "episodes": row[2],
        "thumbnail": row[3],
        "episodes_watched": row[4],
        "score": row[5]
    } for row in result.fetchall()]
