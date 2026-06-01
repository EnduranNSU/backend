package domain

import (
	"context"
)

// TrainingRepository определяет методы для работы с тренировками
type TrainingRepository interface {
	// ========== Planned Trainings ==========
	GetPlannedTrainings(ctx context.Context, userID int) ([]*PlannedTraining, error)
	GetPlannedTraining(ctx context.Context, trainingID int) (*PlannedTraining, error)
	CreatePlannedTraining(ctx context.Context, params CreatePlannedTrainingParams) (*PlannedTraining, error)
	UpdatePlannedTraining(ctx context.Context, trainingID int, params CreatePlannedTrainingParams) (*PlannedTraining, error)
	DeletePlannedTraining(ctx context.Context, trainingID int) error

	// ========== User Performed Trainings ==========
	GetUserPerformedTrainings(ctx context.Context, userID int) ([]*UserPerformedTraining, error)
	GetUserPerformedTraining(ctx context.Context, trainingID int) (*UserPerformedTraining, error)
	CreateUserPerformedTraining(ctx context.Context, params CreateUserPerformedTrainingParams) (*UserPerformedTraining, error)
	UpdateUserPerformedTraining(ctx context.Context, trainingID int, params CreateUserPerformedTrainingParams) (*UserPerformedTraining, error)
	DeleteUserPerformedTraining(ctx context.Context, trainingID int) error
}
