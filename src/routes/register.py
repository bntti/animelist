from typing import Union

from flask import Blueprint, Response, flash, redirect, render_template, request

from services import user_service

register_bp = Blueprint("register", __name__)


@register_bp.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    username = ""
    password1 = ""
    password2 = ""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        errors = user_service.register(username, password1, password2)
        if not errors:
            flash("Account created")
            return redirect("/")
        for error in errors:
            flash(error, "error")

    return render_template(
        "register.html", username=username, password1=password1, password2=password2
    )
