from flask import Blueprint, Response, flash, redirect, request

from services import user_service

logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout")
def logout() -> Response:
    user_service.logout()
    flash("Logged out")
    return redirect(request.referrer)
