from flask import Blueprint, flash, render_template, request, session

from repositories import (
    anime_repository,
    list_repository,
    relation_repository,
    tag_repository,
)
from services import list_service, user_service

anime_bp = Blueprint("anime", __name__)


@anime_bp.route("/anime/<int:anime_id>", methods=["GET"])
def anime_get(anime_id: int) -> str:
    anime = anime_repository.get_anime(anime_id)
    if not anime:
        return render_template("anime.html", anime=anime)

    user_data = {"in_list": False, "score": None}
    if "user_id" in session:
        new_data = list_repository.get_user_anime_data(session["user_id"], anime_id)
        user_data = new_data if new_data else user_data

    related_anime = relation_repository.get_anime_related_anime(anime_id)
    anime_tags = tag_repository.get_tags(anime_id)

    return render_template(
        "anime.html",
        anime=anime,
        user_data=user_data,
        related_anime=related_anime,
        tags=anime_tags,
    )


@anime_bp.route("/anime/<int:anime_id>", methods=["POST"])
def anime_post(anime_id: int) -> str:
    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])

    anime = anime_repository.get_anime(anime_id)
    if not anime:
        return anime_get(anime_id)

    # Anime is removed from list
    if request.form["submit"] == "Remove from list":
        list_repository.remove_from_list(session["user_id"], anime_id)
        flash("Anime removed from list")
        return anime_get(anime_id)

    # Anime is added to list
    if request.form["submit"] == "Add to list":
        flash("Anime added to list")
        list_repository.add_to_list(session["user_id"], anime_id)

    # Handle anime user data change
    list_service.handle_change(
        anime["id"],
        request.form.get("times_watched"),
        request.form.get("episodes_watched"),
        request.form.get("status"),
        request.form.get("score"),
    )

    if request.form["submit"] != "Add to list":
        flash("Updated anime data")

    return anime_get(anime_id)
