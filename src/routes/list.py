from flask import Blueprint, abort, flash, render_template, request, session

from repositories import list_repository, user_repository
from routes.template_filter import url_encode
from services import list_service, user_service

list_bp = Blueprint("list", __name__)


@list_bp.route("/list/<path:username>", methods=["GET"])
def list_get(username: str) -> str:
    user_data = user_repository.get_user_data(username)
    if not user_data:
        return "<h1>No user found<h1>"
    user_id, _ = user_data
    own_profile = "user_id" in session and session["user_id"] == user_id

    tag = request.args["tag"] if "tag" in request.args else ""
    status = request.args["status"] if "status" in request.args else "All"
    list_data = list_repository.get_list_data(user_id, status, tag)
    base_url = f"/list/{url_encode(username)}?"
    status_url = f"{base_url}status={status}"
    base_url = base_url if not tag else f"{base_url}tag={tag}&"

    return render_template(
        "list.html",
        base_url=base_url,
        status_url=status_url,
        tag=tag,
        username=username,
        own_profile=own_profile,
        list_data=list_data,
        status=status,
    )


@list_bp.route("/list/<path:username>", methods=["POST"])
def list_post(username: str) -> str:
    user_data = user_repository.get_user_data(username)
    if not user_data:
        return list_get(username)
    user_id, _ = user_data

    user_service.check_user()
    user_service.check_csrf(request.form["csrf_token"])
    if "user_id" not in session or session["user_id"] != user_id:
        abort(403)

    tag = request.args["tag"] if "tag" in request.args else ""
    status = request.args["status"] if "status" in request.args else "All"
    list_data = list_repository.get_list_data(user_id, status, tag)

    # Handle list data change
    for anime in list_data:
        if request.form.get(f"remove_{anime['id']}"):
            list_repository.remove_from_list(user_id, anime["id"])
        else:
            list_service.handle_change(
                anime["id"],
                None,
                request.form[f"episodes_watched_{anime['id']}"],
                request.form[f"status_{anime['id']}"],
                request.form[f"score_{anime['id']}"],
            )

    flash("List updated")
    return list_get(username)
