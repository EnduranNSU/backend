package postgres

import (
	"context"
	"errors"
	"fmt"

	"github.com/EnduranNSU/exercise/internal/domain"
	"github.com/EnduranNSU/exercise/internal/logging"
	"github.com/EnduranNSU/exercise/internal/minio"
	"gorm.io/gorm"
)

type exerciseRepositoryGorm struct {
	db       *gorm.DB
	s3Client *minio.S3Client
}

func NewExerciseRepositoryGorm(db *gorm.DB, s3Client *minio.S3Client) domain.ExerciseRepository {
	return &exerciseRepositoryGorm{
		db:       db,
		s3Client: s3Client,
	}
}

func (r *exerciseRepositoryGorm) CreateExercise(ctx context.Context, params domain.ExerciseCreate) (*domain.ExerciseRead, error) {
	operation := "CreateExercise"
	logData := map[string]interface{}{
		"title": params.Title,
		"tags":  params.Tags,
		"hrefs": params.Hrefs,
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Creating exercise")

	// Create exercise model
	exercise := Exercise{
		Title: params.Title,
		Tags:  params.Tags,
		Hrefs: params.Hrefs,
	}

	// Use transaction for data consistency
	err := r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		// Save to database
		if err := tx.Create(&exercise).Error; err != nil {
			logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to create exercise in database")
			return fmt.Errorf("failed to create exercise: %w", err)
		}

		// Upload description to S3
		if err := r.s3Client.UploadExerciseDescription(ctx, int(exercise.ID), params.Description); err != nil {
			logging.Error(err, operation, logging.MarshalLogData(logData),
				"Failed to upload exercise description to S3")
			return fmt.Errorf("failed to upload exercise description: %w", err)
		}

		return nil
	})

	if err != nil {
		return nil, err
	}

	logData["exercise_id"] = exercise.ID
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully created exercise")

	// Return the created exercise
	return &domain.ExerciseRead{
		ID:    int(exercise.ID),
		Title: exercise.Title,
		Tags:  exercise.Tags,
		Hrefs: exercise.Hrefs,
	}, nil
}

func (r *exerciseRepositoryGorm) GetExercises(ctx context.Context) ([]*domain.ExerciseRead, error) {
	operation := "GetExercises"
	logData := map[string]interface{}{}

	logging.Debug(operation, logging.MarshalLogData(logData), "Fetching all exercises")

	var exercises []Exercise
	err := r.db.WithContext(ctx).Find(&exercises).Error
	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to fetch exercises")
		return nil, fmt.Errorf("failed to get exercises: %w", err)
	}

	// Convert to domain models
	exerciseReads := make([]*domain.ExerciseRead, 0, len(exercises))
	for _, exercise := range exercises {
		exerciseReads = append(exerciseReads, &domain.ExerciseRead{
			ID:    int(exercise.ID),
			Title: exercise.Title,
			Tags:  exercise.Tags,
			Hrefs: exercise.Hrefs,
		})
	}

	logData["count"] = len(exerciseReads)
	logging.Info(operation, logging.MarshalLogData(logData), "Successfully fetched exercises")

	return exerciseReads, nil
}

func (r *exerciseRepositoryGorm) GetExerciseById(ctx context.Context, exerciseId int) (*domain.ExerciseReadVerbose, error) {
	operation := "GetExerciseById"
	logData := map[string]interface{}{
		"exercise_id": exerciseId,
	}

	logging.Debug(operation, logging.MarshalLogData(logData), "Fetching exercise by ID")

	var exercise Exercise
	err := r.db.WithContext(ctx).First(&exercise, exerciseId).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			logging.Debug(operation, logging.MarshalLogData(logData), "Exercise not found")
			return nil, nil
		}
		logging.Error(err, operation, logging.MarshalLogData(logData), "Failed to fetch exercise")
		return nil, fmt.Errorf("failed to get exercise by ID: %w", err)
	}

	// Download description from S3
	description, err := r.s3Client.DownloadExerciseDescription(ctx, exerciseId)
	if err != nil {
		logging.Error(err, operation, logging.MarshalLogData(logData),
			"Failed to download exercise description from S3")
		return nil, fmt.Errorf("failed to download exercise description: %w", err)
	}

	logging.Info(operation, logging.MarshalLogData(logData), "Successfully fetched exercise")

	// Return the verbose exercise
	return &domain.ExerciseReadVerbose{
		ID:          int(exercise.ID),
		Title:       exercise.Title,
		Tags:        exercise.Tags,
		Hrefs:       exercise.Hrefs,
		Description: description,
	}, nil
}
