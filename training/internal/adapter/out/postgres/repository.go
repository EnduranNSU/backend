package postgres

import (
	"context"
	"errors"
	"fmt"

	"github.com/EnduranNSU/trainings/internal/domain"
	"github.com/EnduranNSU/trainings/internal/logging"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

type trainingRepositoryGorm struct {
	db *gorm.DB
}

func NewTrainingRepositoryGorm(db *gorm.DB) domain.TrainingRepository {
	return &trainingRepositoryGorm{
		db: db,
	}
}

func (r *trainingRepositoryGorm) GetPlannedTrainings(ctx context.Context, userID int) ([]*domain.PlannedTraining, error) {
	operation := "GetPlannedTrainings"
	logData := map[string]interface{}{
		"user_id": userID,
	}

	logging.Debug(operation, logging.MarshalLogData(logData), "Fetching planned trainings")

	var plannedTrainings []PlannedTraining

	err := r.db.WithContext(ctx).
		Preload("Training.PerfomableExercises.Exercise").
		Preload("Training.PerfomableExercises.Sets").
		Where("user_id = ?", userID).
		Find(&plannedTrainings).Error

	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to fetch planned trainings")
		return nil, fmt.Errorf("failed to get planned trainings: %w", err)
	}

	result := make([]*domain.PlannedTraining, len(plannedTrainings))
	for i, pt := range plannedTrainings {
		result[i] = r.toDomainPlannedTraining(&pt)
	}

	logData["count"] = len(result)
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully fetched planned trainings")

	return result, nil
}

func (r *trainingRepositoryGorm) GetPlannedTraining(ctx context.Context, trainingID int) (*domain.PlannedTraining, error) {
	operation := "GetPlannedTraining"
	logData := map[string]interface{}{
		"training_id": trainingID,
	}

	logging.Debug(operation, logging.MarshalLogData(logData), "Fetching planned training")

	var plannedTraining PlannedTraining

	err := r.db.WithContext(ctx).
		Preload("Training.PerfomableExercises.Exercise").
		Preload("Training.PerfomableExercises.Sets").
		First(&plannedTraining, trainingID).Error

	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			logging.Debug(operation, logging.MarshalLogData(logData), "Planned training not found")
			return nil, nil
		}
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to fetch planned training")
		return nil, fmt.Errorf("failed to get planned training: %w", err)
	}

	result := r.toDomainPlannedTraining(&plannedTraining)
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully fetched planned training")

	return result, nil
}

func (r *trainingRepositoryGorm) CreatePlannedTraining(ctx context.Context, params domain.CreatePlannedTrainingParams) (*domain.PlannedTraining, error) {
	operation := "CreatePlannedTraining"
	logData := map[string]interface{}{
		"user_id":  params.UserID,
		"weekdays": params.Weekdays,
		"training": map[string]interface{}{
			"title":           params.Training.Title,
			"exercises_count": len(params.Training.PerfomableExercises),
		},
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Creating planned training")

	// Создаем тренировку
	training := &Training{
		Title: params.Training.Title,
	}

	// Создаем выполняемые упражнения
	for _, pe := range params.Training.PerfomableExercises {
		perfExercise := &PerfomableExercise{
			ExerciseID: uint(pe.ExerciseID),
		}

		// Создаем сеты для упражнения
		for _, s := range pe.Sets {
			set := &Set{
				Weight:       s.Weight,
				Repetitions:  s.Repetitions,
				RestDuration: s.RestDuration,
			}
			perfExercise.Sets = append(perfExercise.Sets, *set)
		}
		training.PerfomableExercises = append(training.PerfomableExercises, *perfExercise)
	}

	// Используем транзакцию
	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Создаем тренировку
		if err := tx.Create(training).Error; err != nil {
			return err
		}

		// Создаем запланированную тренировку
		plannedTraining := &PlannedTraining{
			UserID:     uint(params.UserID),
			TrainingID: training.ID,
			Weekdays:   params.Weekdays,
		}

		if err := tx.Create(plannedTraining).Error; err != nil {
			return err
		}

		return nil
	})

	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to create planned training")
		return nil, fmt.Errorf("failed to create planned training: %w", err)
	}

	logData["training_id"] = training.ID
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully created planned training")

	// Возвращаем созданную тренировку
	return r.GetPlannedTraining(ctx, int(training.ID))
}

func (r *trainingRepositoryGorm) UpdatePlannedTraining(ctx context.Context, trainingID int, params domain.CreatePlannedTrainingParams) (*domain.PlannedTraining, error) {
	operation := "UpdatePlannedTraining"
	logData := map[string]interface{}{
		"training_id": trainingID,
		"user_id":     params.UserID,
		"weekdays":    params.Weekdays,
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Updating planned training")

	// Удаляем старую и создаем новую в транзакции
	var newPlannedTraining *domain.PlannedTraining

	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Получаем существующую запланированную тренировку
		var existing PlannedTraining
		if err := tx.Preload("Training").First(&existing, trainingID).Error; err != nil {
			return err
		}

		// Удаляем связанные данные (каскадно)
		if err := tx.Select(clause.Associations).Delete(&existing).Error; err != nil {
			return err
		}

		// Создаем новую
		var err error
		newPlannedTraining, err = r.CreatePlannedTraining(ctx, params)
		return err
	})

	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to update planned training")
		return nil, fmt.Errorf("failed to update planned training: %w", err)
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Successfully updated planned training")
	return newPlannedTraining, nil
}

func (r *trainingRepositoryGorm) DeletePlannedTraining(ctx context.Context, trainingID int) error {
	operation := "DeletePlannedTraining"
	logData := map[string]interface{}{
		"training_id": trainingID,
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Deleting planned training")

	// Используем транзакцию для каскадного удаления
	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		var plannedTraining PlannedTraining
		if err := tx.Preload("Training.PerfomableExercises.Sets").First(&plannedTraining, trainingID).Error; err != nil {
			return err
		}

		// Удаляем все связанные данные
		if err := tx.Select(clause.Associations).Delete(&plannedTraining).Error; err != nil {
			return err
		}

		return nil
	})

	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			logging.Warn(operation, logging.MarshalLogData(logData), "Planned training not found for deletion")
			return nil
		}
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to delete planned training")
		return fmt.Errorf("failed to delete planned training: %w", err)
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Successfully deleted planned training")
	return nil
}

// ========== User Performed Trainings ==========

func (r *trainingRepositoryGorm) GetUserPerformedTrainings(ctx context.Context, userID int) ([]*domain.UserPerformedTraining, error) {
	operation := "GetUserPerformedTrainings"
	logData := map[string]interface{}{
		"user_id": userID,
	}

	logging.Debug(operation, logging.MarshalLogData(logData), "Fetching performed trainings")

	var performedTrainings []UserPerformedTraining

	err := r.db.WithContext(ctx).
		Preload("Training.PerfomableExercises.Exercise").
		Preload("Training.PerfomableExercises.Sets").
		Where("user_id = ?", userID).
		Find(&performedTrainings).Error

	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to fetch performed trainings")
		return nil, fmt.Errorf("failed to get performed trainings: %w", err)
	}

	result := make([]*domain.UserPerformedTraining, len(performedTrainings))
	for i, pt := range performedTrainings {
		result[i] = r.toDomainPerformedTraining(&pt)
	}

	logData["count"] = len(result)
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully fetched performed trainings")

	return result, nil
}

func (r *trainingRepositoryGorm) GetUserPerformedTraining(ctx context.Context, trainingID int) (*domain.UserPerformedTraining, error) {
	operation := "GetUserPerformedTraining"
	logData := map[string]interface{}{
		"training_id": trainingID,
	}

	logging.Debug(operation, logging.MarshalLogData(logData), "Fetching performed training")

	var performedTraining UserPerformedTraining

	err := r.db.WithContext(ctx).
		Preload("Training.PerfomableExercises.Exercise").
		Preload("Training.PerfomableExercises.Sets").
		First(&performedTraining, trainingID).Error

	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			logging.Debug(operation, logging.MarshalLogData(logData), "Performed training not found")
			return nil, nil
		}
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to fetch performed training")
		return nil, fmt.Errorf("failed to get performed training: %w", err)
	}

	result := r.toDomainPerformedTraining(&performedTraining)
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully fetched performed training")

	return result, nil
}

func (r *trainingRepositoryGorm) CreateUserPerformedTraining(ctx context.Context, params domain.CreateUserPerformedTrainingParams) (*domain.UserPerformedTraining, error) {
	operation := "CreateUserPerformedTraining"
	logData := map[string]interface{}{
		"user_id": params.UserID,
		"date":    params.Date,
		"training": map[string]interface{}{
			"title":           params.Training.Title,
			"exercises_count": len(params.Training.PerfomableExercises),
		},
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Creating performed training")

	// Создаем тренировку
	training := &Training{
		Title: params.Training.Title,
	}

	// Создаем выполняемые упражнения
	for _, pe := range params.Training.PerfomableExercises {
		perfExercise := &PerfomableExercise{
			ExerciseID: uint(pe.ExerciseID),
		}

		// Создаем сеты для упражнения
		for _, s := range pe.Sets {
			set := &Set{
				Weight:       s.Weight,
				Repetitions:  s.Repetitions,
				RestDuration: s.RestDuration,
			}
			perfExercise.Sets = append(perfExercise.Sets, *set)
		}
		training.PerfomableExercises = append(training.PerfomableExercises, *perfExercise)
	}

	// Используем транзакцию
	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Создаем тренировку
		if err := tx.Create(training).Error; err != nil {
			return err
		}

		// Создаем выполненную тренировку
		performedTraining := &UserPerformedTraining{
			UserID:     uint(params.UserID),
			TrainingID: training.ID,
			Date:       params.Date,
		}

		if err := tx.Create(performedTraining).Error; err != nil {
			return err
		}

		return nil
	})

	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to create performed training")
		return nil, fmt.Errorf("failed to create performed training: %w", err)
	}

	logData["training_id"] = training.ID
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully created performed training")

	// Возвращаем созданную тренировку
	return r.GetUserPerformedTraining(ctx, int(training.ID))
}

func (r *trainingRepositoryGorm) UpdateUserPerformedTraining(ctx context.Context, trainingID int, params domain.CreateUserPerformedTrainingParams) (*domain.UserPerformedTraining, error) {
	operation := "UpdateUserPerformedTraining"
	logData := map[string]interface{}{
		"training_id": trainingID,
		"user_id":     params.UserID,
		"date":        params.Date,
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Updating performed training")

	var newPerformedTraining *domain.UserPerformedTraining

	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		var existing UserPerformedTraining
		if err := tx.Preload("Training").First(&existing, trainingID).Error; err != nil {
			return err
		}

		if err := tx.Select(clause.Associations).Delete(&existing).Error; err != nil {
			return err
		}

		var err error
		newPerformedTraining, err = r.CreateUserPerformedTraining(ctx, params)
		return err
	})

	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to update performed training")
		return nil, fmt.Errorf("failed to update performed training: %w", err)
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Successfully updated performed training")
	return newPerformedTraining, nil
}

func (r *trainingRepositoryGorm) DeleteUserPerformedTraining(ctx context.Context, trainingID int) error {
	operation := "DeleteUserPerformedTraining"
	logData := map[string]interface{}{
		"training_id": trainingID,
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Deleting performed training")

	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		var performedTraining UserPerformedTraining
		if err := tx.Preload("Training.PerfomableExercises.Sets").First(&performedTraining, trainingID).Error; err != nil {
			return err
		}

		if err := tx.Select(clause.Associations).Delete(&performedTraining).Error; err != nil {
			return err
		}

		return nil
	})

	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			logging.Warn(operation, logging.MarshalLogData(logData), "Performed training not found for deletion")
			return nil
		}
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to delete performed training")
		return fmt.Errorf("failed to delete performed training: %w", err)
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Successfully deleted performed training")
	return nil
}
