package domain

import (
	"context"
)

type ExerciseRepository interface {
	CreateExercise(ctx context.Context, params ExerciseCreate) (*ExerciseRead, error)
	GetExercises(ctx context.Context) ([]*ExerciseRead, error)
	GetExerciseById(ctx context.Context, exerciseId int) (*ExerciseReadVerbose, error)
}
