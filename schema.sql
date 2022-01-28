CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    salt TEXT NOT NULL,
    password TEXT NOT NULL
);
CREATE TABLE animes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    episodes INT NOT NULL,
    link TEXT NOT NULL,
    picture TEXT NOT NULL,
    thumbnail TEXT NOT NULL
)