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


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/animes")
def animes() -> str:
    animes = database.get_anime(0)
    return render_template("animes.html", animes=animes)


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
