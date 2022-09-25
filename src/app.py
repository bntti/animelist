from flask import Flask

from config import SECRET_KEY, URL
from database import database
from routes import (
    anime,
    index,
    list,
    login,
    logout,
    profile,
    register,
    tags,
    template_filter,
    topanime,
)


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 1024**2
    app.config["SQLALCHEMY_DATABASE_URI"] = URL

    database.init_app(app)

    app.register_blueprint(template_filter.template_filter_bp)
    app.register_blueprint(anime.anime_bp)
    app.register_blueprint(index.index_bp)
    app.register_blueprint(list.list_bp)
    app.register_blueprint(login.login_bp)
    app.register_blueprint(logout.logout_bp)
    app.register_blueprint(profile.profile_bp)
    app.register_blueprint(register.register_bp)
    app.register_blueprint(tags.tags_bp)
    app.register_blueprint(topanime.topanime_bp)

    return app
