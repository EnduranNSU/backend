-- name: CreateUser :one
INSERT INTO users (email, name, hashed_password)
VALUES ($1, $2, $3)
RETURNING id, email, name, hashed_password;

-- name: GetUserByEmail :one
SELECT id, email, name, hashed_password
FROM users
WHERE email = $1
LIMIT 1;

-- name: GetUserByID :one
SELECT id, email, name, hashed_password
FROM users
WHERE id = $1
LIMIT 1;

-- name: CheckUserExistsByEmail :one
SELECT EXISTS(
    SELECT 1 FROM users WHERE email = $1
);