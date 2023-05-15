from flask import Blueprint, abort, flash, render_template, request, session

from repositories import list_repository, user_repository
from routes.template_filter import url_encode
from services import list_service, user_service

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile/<path:username>", methods=["GET"])
def profile_get(username: str) -> str:
    user_data = user_repository.get_user_data(username)
    if not user_data:
        return "<h1>No user found<h1>"
    user_id, _ = user_data
    own_profile = "user_id" in session and session["user_id"] == user_id
    counts = list_repository.get_counts(user_id)
    tags = request.args["tags"] if "tags" in request.args else ""
    if tags != "top":
        sorted_tags = list_repository.get_watched_tags(user_id)
    else:
        sorted_tags = list_repository.get_popular_tags(user_id)
    return render_template(
        "profile.html",
        tags=tags,
        own_profile=own_profile,
        username=username,
        list_url=f"/list/{url_encode(username)}",
        counts=counts,
        sorted_tags=sorted_tags,
    )


@profile_bp.route("/profile/<path:username>", methods=["POST"])
def profile_post(username: str) -> str:
    user_data = user_repository.get_user_data(username)
    if not user_data:
        return profile_get(username)
    user_id, _ = user_data

    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    if "user_id" not in session or session["user_id"] != user_id:
        abort(403)

    # Import from myanimelist
    if "mal_import" in request.files:
        file = request.files["mal_import"]
        list_service.import_from_myanimelist(file)
        return profile_get(username)

    # "Show hidden" setting change
    new_show_hidden = bool(request.form.get("show hidden"))
    if new_show_hidden != session["show_hidden"]:
        session["show_hidden"] = new_show_hidden
        user_repository.set_show_hidden(new_show_hidden)
        flash("Settings updated")

    return profile_get(username)
