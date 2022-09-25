import os

from dotenv import load_dotenv

dirname = os.path.dirname(__file__)
try:
    load_dotenv(dotenv_path=os.path.join(dirname, "..", ".env"))
except FileNotFoundError:
    pass

URL = os.getenv("DATABASE_URL")
if URL.startswith("postgres://"):
    URL = URL.replace("postgres://", "postgresql://", 1)

SECRET_KEY = os.getenv("SECRET_KEY")
