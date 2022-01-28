from typing import Union
from os import getenv
from flask import Flask, Response
from flask import render_template, request, session, redirect
from database import DB
import functions

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database = DB(app)

ANIME_COUNT = database.anime_count()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/animes")
def animes() -> str:
    if "page" in request.args and request.args["page"].isdigit():
        page = int(request.args["page"])
    else:
        page = 0

    page = max(0, min(ANIME_COUNT - 50, page))
    prev_page = max(page - 50, 0)
    next_page = min(page + 50, ANIME_COUNT - 50)
    animes = database.get_anime(page)
    return render_template(
        "animes.html",
        animes=animes,
        prev_url=f"/animes?page={prev_page}",
        next_url=f"/animes?page={next_page}"
    )


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = functions.login(database, username, password)
        if error == "OK":
            session["user"] = {"username": request.form["username"]}
            return redirect("/")

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register() -> Union[str, Response]:
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        error = functions.register(database, username, password1, password2)
        if error == "OK":
            database.add_user(username, password1)
            session["user"] = {"username": request.form["username"]}
            return redirect("/")
    return render_template("register.html", error=error)


@app.route("/logout")
def logout() -> Response:
    if "user" in session:
        del session["user"]
    return redirect("/")
