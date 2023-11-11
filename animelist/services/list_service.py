from typing import Optional

from defusedxml.ElementTree import ParseError, fromstring
from flask import abort, flash, session
from werkzeug.datastructures import FileStorage
from werkzeug.wrappers.response import Response

from repositories import anime_repository, list_repository


# Helper functions
def import_from_myanimelist(file: FileStorage) -> None:
    try:
        root = fromstring(file.read())
    except ParseError:
        abort(Response("Error parsing XML file", 415))

    error = False
    for node in root:
        if node.tag == "anime":
            title = ""
            try:
                title = node.find("./series_title").text
                title = title.replace("\t", "").replace("\n", "")
                anime = {
                    "id": node.find("./series_animedb_id").text,
                    "episodes": int(node.find("./my_watched_episodes").text),
                    "score": int(node.find("./my_score").text),
                    "status": node.find("./my_status").text,
                    "times_watched": int(node.find("./my_times_watched").text),
                }
                if anime["status"] == "Completed":
                    anime["times_watched"] += 1
                assert import_to_list(session["user_id"], anime)
            except (AttributeError, ValueError, AssertionError):
                error = True
                if title:
                    flash(f"Failed to import anime '{title}'", "error")
                else:
                    flash("Failed to import an anime that is missing a title", "error")

    if not error:
        flash("Data imported from MyAnimeList")


def import_to_list(user_id: int, anime: dict) -> bool:
    result = anime_repository.get_anime_id_and_episodes(
        f"https://myanimelist.net/anime/{anime['id']}"
    )

    if not result:
        return False

    anime_id, episodes = result
    anime_data = {**anime, "anime_id": anime_id}

    # Check data
    if (
        not 0 <= anime["episodes"] <= episodes
        or not 0 <= anime["score"] <= 10
        or anime["status"]
        not in ["Completed", "Watching", "On-Hold", "Dropped", "Plan to Watch"]
        or not 0 <= anime["times_watched"] <= 1000
    ):
        return False

    # If score is 0, then score has not yet been set
    anime_data["score"] = None if int(anime_data["score"]) == 0 else anime_data["score"]

    list_repository.import_to_list(user_id, anime_data)
    return True


def handle_change(
    anime_id: int,
    new_times_watched: Optional[str],
    new_episodes_watched: str,
    new_status: str,
    new_score: str,
) -> None:
    user_id = session["user_id"]
    user_data = list_repository.get_user_anime_data(user_id, anime_id)
    anime = anime_repository.get_anime(anime_id)

    if (
        new_times_watched
        and str.isdigit(new_times_watched)
        and 0 <= int(new_times_watched) <= 1000
    ):
        times_watched = int(new_times_watched)
        if times_watched != user_data["times_watched"]:
            list_repository.set_times_watched(user_id, anime_id, times_watched)

    if (
        new_episodes_watched
        and str.isdigit(new_episodes_watched)
        and 0 <= int(new_episodes_watched) <= anime["episodes"]
    ):
        episodes_watched = int(new_episodes_watched)
        if episodes_watched != user_data["episodes"]:
            user_data["episodes"] = episodes_watched
            list_repository.set_episodes_watched(user_id, anime_id, episodes_watched)
            if episodes_watched == anime["episodes"]:
                list_repository.set_status(user_id, anime_id, "Completed")
                list_repository.add_times_watched(user_id, anime_id, 1)
            else:
                list_repository.set_status(user_id, anime_id, "Watching")

    if new_status in ["Completed", "Watching", "On-Hold", "Dropped", "Plan to Watch"]:
        if new_status != user_data["status"]:
            list_repository.set_status(user_id, anime_id, new_status)
            if new_status == "Completed" and user_data["episodes"] != anime["episodes"]:
                list_repository.set_episodes_watched(
                    user_id, anime_id, anime["episodes"]
                )
                list_repository.add_times_watched(user_id, anime_id, 1)

    if new_score == "None" or (str.isdigit(new_score) and 1 <= int(new_score) <= 10):
        score = None if new_score == "None" else int(new_score)
        if score != user_data["score"]:
            list_repository.set_score(user_id, anime_id, score)
