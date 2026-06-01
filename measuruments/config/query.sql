-- name: CreateMeasurement :one
INSERT INTO measurements (
    user_id,
    type,
    value,
    date
) VALUES (
    $1, $2, $3, $4
)
RETURNING id, user_id, type, value, date;

-- name: GetMeasurementsByUser :many
SELECT id, user_id, type, value, date
FROM measurements
WHERE user_id = $1
ORDER BY date DESC;

-- name: DeleteMeasurementsByUser :exec
DELETE FROM measurements
WHERE user_id = $1;