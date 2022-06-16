from typing import Optional

from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from database import database


# Database functions
def add_to_list(user_id: int, anime_id: int) -> None:
    try:
        sql = "INSERT INTO list (user_id, anime_id) VALUES (:user_id, :anime_id)"
        database.session.execute(sql, {"user_id": user_id, "anime_id": anime_id})
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()


def import_to_list(user_id: int, anime_data: dict) -> bool:
    try:
        sql = """
            INSERT INTO list (user_id, anime_id, episodes, score, status, times_watched)
            VALUES (:user_id, :anime_id, :episodes, :score, :status, :times_watched)
        """
        database.session.execute(sql, {**anime_data, "user_id": user_id})
        database.session.commit()
    except IntegrityError as error:
        # UNIQUE constraint fail
        assert isinstance(error.orig, UniqueViolation)
        database.session.rollback()
    return True


def remove_from_list(user_id: int, anime_id: int) -> None:
    sql = "DELETE FROM list WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(sql, {"user_id": user_id, "anime_id": anime_id})
    database.session.commit()


def set_score(user_id: int, anime_id: int, score: Optional[int]) -> None:
    sql = "UPDATE list SET score = :score WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id, "score": score}
    )
    database.session.commit()


def set_times_watched(user_id: int, anime_id: int, times_watched: int) -> None:
    sql = """
        UPDATE list SET times_watched = :times_watched
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id, "times_watched": times_watched}
    )
    database.session.commit()


def add_times_watched(user_id: int, anime_id: int, add: int) -> None:
    sql = """
        UPDATE list SET times_watched = times_watched + :add
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id, "add": add}
    )
    database.session.commit()


def set_status(user_id: int, anime_id: int, status: str) -> None:
    sql = "UPDATE list SET status = :status WHERE user_id = :user_id AND anime_id = :anime_id"
    database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id, "status": status}
    )
    database.session.commit()


def set_episodes_watched(user_id: int, anime_id: int, episodes_watched: int) -> None:
    sql = """
        UPDATE list SET episodes = :episodes_watched
        WHERE user_id = :user_id AND anime_id = :anime_id
    """

    database.session.execute(
        sql,
        {
            "user_id": user_id,
            "anime_id": anime_id,
            "episodes_watched": episodes_watched,
        },
    )
    database.session.commit()


def get_user_anime_data(user_id: int, anime_id: int) -> Optional[dict]:
    sql = """
        SELECT score, episodes, status, times_watched
        FROM list
        WHERE user_id = :user_id AND anime_id = :anime_id
    """
    row = database.session.execute(
        sql, {"user_id": user_id, "anime_id": anime_id}
    ).fetchone()

    return (
        None
        if not row
        else {
            "score": row[0],
            "episodes": row[1],
            "status": row[2],
            "times_watched": row[3],
            "in_list": True,
        }
    )


def get_counts(user_id: int) -> dict:
    sql = """
        SELECT 
            COUNT(*),
            COUNT(CASE WHEN status LIKE 'Completed' THEN 1 END),
            COUNT(CASE WHEN status LIKE 'Watching' THEN 1 END),
            COUNT(CASE WHEN status LIKE 'On-Hold' THEN 1 END),
            COUNT(CASE WHEN status LIKE 'Dropped' THEN 1 END),
            COUNT(CASE WHEN status LIKE 'Plan to Watch' THEN 1 END)
        FROM list
        WHERE user_id = :user_id
    """
    row = database.session.execute(sql, {"user_id": user_id}).fetchone()
    return {
        "total": row[0],
        "completed": row[1],
        "watching": row[2],
        "on_hold": row[3],
        "dropped": row[4],
        "plan_to_watch": row[5],
    }


def get_watched_tags(user_id: int) -> list:
    sql = """
        SELECT t.tag, COUNT(l.id)
        FROM list l, tags t
        WHERE user_id = :user_id AND t.anime_id = l.anime_id
        GROUP BY t.tag
        ORDER BY COUNT(l.id) DESC, t.tag
    """
    result = database.session.execute(sql, {"user_id": user_id}).fetchall()
    return result


def get_popular_tags(user_id: int) -> list:
    sql = """
        SELECT t.tag, ROUND(AVG(l.score), 2)
        FROM list l, tags t
        WHERE user_id = :user_id AND t.anime_id = l.anime_id
        GROUP BY t.tag
        ORDER BY COALESCE(AVG(l.score), 0) DESC, t.tag
    """
    result = database.session.execute(sql, {"user_id": user_id}).fetchall()
    return result


def get_list_ids(user_id: int) -> list:
    sql = "SELECT anime_id FROM list WHERE user_id = :user_id"
    result = database.session.execute(sql, {"user_id": user_id})
    return [row[0] for row in result.fetchall()]


def get_list_data(user_id: int, status: str, tag: str) -> list:
    sql = """
        SELECT a.id, a.thumbnail, a.title, l.episodes, a.episodes, l.status, l.score
        FROM list l, anime a, tags t
        WHERE l.anime_id = a.id AND t.anime_id = a.id AND l.user_id = :user_id
            AND (:tag = '' OR t.tag = :tag) AND (l.status = :status OR :status = 'All')
        GROUP BY a.id, l.id ORDER BY a.title
    """

    result = database.session.execute(
        sql, {"user_id": user_id, "status": status, "tag": tag}
    )

    return [
        {
            "id": row[0],
            "thumbnail": row[1],
            "title": row[2],
            "episodes_watched": row[3],
            "episodes": row[4],
            "status": row[5],
            "score": row[6],
        }
        for row in result.fetchall()
    ]
