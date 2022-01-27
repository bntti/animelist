CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    salt TEXT NOT NULL,
    password TEXT NOT NULL
);