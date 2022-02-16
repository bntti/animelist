from typing import Optional
from database import database


def anime_count(query: str) -> int:
    if not query:
        sql = "SELECT COUNT(*) FROM animes WHERE NOT hidden"
    else:
        sql = "SELECT COUNT(DISTINCT a.id) FROM animes a, synonyms s " \
              "WHERE NOT a.hidden AND a.id = s.anime_id AND " \
              "(a.title ILIKE :query OR s.synonym ILIKE :query)"
    row = database.session.execute(sql, {"query": f"%{query}%"}).fetchone()
    return row[0] if row else 0


def add_anime(anime: dict) -> int:
    sql = "INSERT INTO animes (title, episodes, link, picture, thumbnail, hidden) " \
          "VALUES (:title, :episodes, :link, :picture, :thumbnail, :hidden) " \
          "Returning id"
    return database.session.execute(sql, anime).fetchone()[0]


def get_anime_id(mal_link: str) -> Optional[int]:
    sql = "SELECT id FROM animes WHERE link = :link"
    row = database.session.execute(sql, {"link": mal_link}).fetchone()
    return None if not row else row[0]


def get_anime(anime_id: int) -> Optional[dict]:
    sql = "SELECT a.id, a.title, a.episodes, ROUND(AVG(l.score), 2), a.picture " \
          "FROM animes a LEFT JOIN list l ON l.anime_id = a.id WHERE a.id = :id GROUP BY a.id"
    row = database.session.execute(sql, {"id": anime_id}).fetchone()
    return None if not row else {
        "id": row[0],
        "title": row[1],
        "episodes": row[2],
        "score": row[3],
        "picture": row[4]
    }


def get_animes(page: int, query: str) -> list:
    if not query:
        sql = "SELECT a.id, a.thumbnail, a.title, a.episodes, ROUND(AVG(l.score), 2) " \
              "FROM animes a LEFT JOIN list l ON l.anime_id = a.id " \
              "WHERE NOT a.hidden GROUP BY a.id " \
              "ORDER BY COALESCE(AVG(l.score), 0) DESC, COUNT(l.id) DESC, a.title " \
              "LIMIT 50 OFFSET :offset"
    else:
        sql = "SELECT a.id, a.thumbnail, a.title, a.episodes, ROUND(AVG(l.score), 2) " \
              "FROM synonyms s, animes a LEFT JOIN list l ON l.anime_id = a.id " \
              "WHERE NOT a.hidden AND a.id = s.anime_id AND " \
              "(a.title ILIKE :query OR s.synonym ILIKE :query) GROUP BY a.id " \
              "ORDER BY COALESCE(AVG(l.score), 0) DESC, COUNT(l.id) DESC, a.title " \
              "LIMIT 50 OFFSET :offset"
    result = database.session.execute(
        sql, {"offset": page, "query": f"%{query}%"}
    )

    return [{
        "id": row[0],
        "thumbnail": row[1],
        "title": row[2],
        "episodes": row[3],
        "score": row[4]
    } for row in result.fetchall()]
