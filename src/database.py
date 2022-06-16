from os import getenv

from flask_sqlalchemy import SQLAlchemy

from app import app

url = getenv("DATABASE_URL")
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = url
database = SQLAlchemy(app)
