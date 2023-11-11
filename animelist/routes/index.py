from flask import Blueprint, render_template

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index() -> str:
    return render_template("index.html")
