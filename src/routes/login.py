from typing import Union

from flask import Blueprint, Response, flash, redirect, render_template, request

from services import user_service

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    username = ""
    password = ""
    previous_url = request.referrer
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        success = user_service.login(username, password)
        if success:
            flash("Logged in")
            return redirect(request.form["previous_url"])
        flash("Wrong username or password", "error")

    return render_template(
        "login.html", username=username, password=password, previous_url=previous_url
    )
