-- Создание таблицы users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    hashed_password VARCHAR NOT NULL
);

-- Создание индекса для users
CREATE INDEX ix_users_id ON users (id);