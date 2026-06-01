-- Создание таблицы measurements
CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    type VARCHAR NOT NULL,
    value INTEGER NOT NULL,
    date VARCHAR NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Создание индекса для measurements
CREATE INDEX ix_measurements_user_id ON measurements (user_id);