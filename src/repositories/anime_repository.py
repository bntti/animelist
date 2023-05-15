from typing import Optional

from flask import session
from sqlalchemy.sql import text

from database import database


def anime_count(query: str, tag: str) -> int:
    if not tag:
        sql = """
            SELECT COUNT(DISTINCT a.id)
            FROM anime a
                LEFT JOIN synonyms s ON s.anime_id = a.id
            WHERE (NOT a.hidden OR :show_hidden) AND (
                :query = '%%' OR a.title ILIKE :query
                OR (s.synonym IS NOT NULL AND s.synonym ILIKE :query)
            )
        """
    else:
        sql = """
            SELECT COUNT(DISTINCT a.id)
            FROM tags t, anime a
                LEFT JOIN synonyms s ON s.anime_id = a.id
            WHERE a.id = t.anime_id AND t.tag = :tag AND (NOT a.hidden OR :show_hidden) AND (
                :query = '%%' OR a.title ILIKE :query
                OR (s.synonym IS NOT NULL AND s.synonym ILIKE :query)
            )
        """

    row = database.session.execute(
        text(sql),
        {
            "query": f"%{query}%",
            "tag": tag,
            "show_hidden": session["show_hidden"]
            if "show_hidden" in session
            else False,
        },
    ).fetchone()
    return row[0] if row else 0


def myanimelist_link_exists(mal_link: str) -> bool:
    sql = "SELECT 1 FROM anime WHERE link = :link"
    row = database.session.execute(text(sql), {"link": mal_link}).fetchone()
    return bool(row)


def get_anime_id(mal_link: str) -> int:
    sql = "SELECT id FROM anime WHERE link = :link"
    row = database.session.execute(text(sql), {"link": mal_link}).fetchone()
    if not row:
        raise Exception("Tried to get id for an anime that doesn't exist")
    return row[0]


def get_anime_id_and_episodes(mal_link: str) -> Optional[tuple]:
    sql = "SELECT id, episodes FROM anime WHERE link = :link"
    row = database.session.execute(text(sql), {"link": mal_link}).fetchone()
    return None if not row else (row[0], row[1])


def get_anime(anime_id: int) -> Optional[dict]:
    sql = """
        SELECT a.id, a.title, a.link, a.episodes, ROUND(AVG(l.score), 2), a.picture
        FROM anime a
            LEFT JOIN list l ON l.anime_id = a.id
        WHERE a.id = :id
        GROUP BY a.id
    """
    row = database.session.execute(text(sql), {"id": anime_id}).fetchone()
    return (
        None
        if not row
        else {
            "id": row[0],
            "title": row[1],
            "link": row[2],
            "episodes": row[3],
            "score": row[4],
            "picture": row[5],
        }
    )


def get_top_anime(page: int, query: str, tag: str) -> list:
    if not tag:
        sql = """
            SELECT a.id, a.thumbnail, a.title, a.episodes, ROUND(AVG(l.score), 2)
            FROM anime a
                LEFT JOIN list l ON l.anime_id = a.id
                LEFT JOIN synonyms s ON s.anime_id = a.id
            WHERE (NOT a.hidden OR :show_hidden) AND (
                :query = '%%' OR a.title ILIKE :query
                OR (s.synonym IS NOT NULL AND s.synonym ILIKE :query)
            )
            GROUP BY a.id
            ORDER BY COALESCE(AVG(l.score), 0) DESC, COUNT(l.id) DESC, a.title
            LIMIT 50
            OFFSET :offset
        """
    else:
        sql = """
            SELECT a.id, a.thumbnail, a.title, a.episodes, ROUND(AVG(l.score), 2)
            FROM tags t, anime a
                LEFT JOIN list l ON l.anime_id = a.id
                LEFT JOIN synonyms s ON s.anime_id = a.id
            WHERE (NOT a.hidden OR :show_hidden) AND a.id = t.anime_id AND t.tag = :tag AND (
                :query = '%%' OR a.title ILIKE :query
                OR (s.synonym IS NOT NULL AND s.synonym ILIKE :query)
            )
            GROUP BY a.id
            ORDER BY COALESCE(AVG(l.score), 0) DESC, COUNT(l.id) DESC, a.title
            LIMIT 50
            OFFSET :offset
            """
    result = database.session.execute(
        text(sql),
        {
            "offset": page,
            "query": f"%{query}%",
            "tag": tag,
            "show_hidden": session["show_hidden"]
            if "show_hidden" in session
            else False,
        },
    )

    return [
        {
            "id": row[0],
            "thumbnail": row[1],
            "title": row[2],
            "episodes": row[3],
            "score": row[4],
        }
        for row in result.fetchall()
    ]
