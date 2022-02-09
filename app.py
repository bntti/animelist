# pylint: skip-file
from flask import Flask
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MAX_CONTENT_LENGTH'] = 1024 ** 2

if getenv("INIT") == "True":
    import init_db
else:
    import routes
