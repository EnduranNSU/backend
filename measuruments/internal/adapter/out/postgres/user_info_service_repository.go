package postgres

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/EnduranNSU/end-user-info/internal/adapter/out/postgres/gen"
	"github.com/EnduranNSU/end-user-info/internal/domain"
	"github.com/EnduranNSU/end-user-info/internal/logging"
)

type MeasurementRepositoryImpl struct {
	db      *sql.DB
	queries *gen.Queries
}

func NewMeasurementRepository(db *sql.DB) domain.MeasurementRepository {
	return &MeasurementRepositoryImpl{
		db:      db,
		queries: gen.New(db),
	}
}

// CreateMeasurement создает новое измерение
func (r *MeasurementRepositoryImpl) CreateMeasurement(ctx context.Context, measurement *domain.MeasurementCreate) (*domain.MeasurementRead, error) {
	params := gen.CreateMeasurementParams{
		UserID: int32(measurement.UserID),
		Type:   measurement.Type,
		Value:  int32(measurement.Value),
		Date:   measurement.Date,
	}

	dbMeasurement, err := r.queries.CreateMeasurement(ctx, params)
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": measurement.UserID,
			"type":    measurement.Type,
			"value":   measurement.Value,
			"date":    measurement.Date,
		})
		logging.Error(err, "CreateMeasurement", jsonData, "failed to create measurement")
		return nil, err
	}

	result := &domain.MeasurementRead{
		MeasurementBase: domain.MeasurementBase{
			Type:  dbMeasurement.Type,
			Value: int(dbMeasurement.Value),
			Date:  dbMeasurement.Date,
		},
		ID: int(dbMeasurement.ID),
	}

	jsonData := logging.MarshalLogData(map[string]interface{}{
		"measurement_id": result.ID,
		"user_id":        measurement.UserID,
		"type":           measurement.Type,
	})
	logging.Debug("CreateMeasurement", jsonData, "successfully created measurement")

	return result, nil
}

// GetMeasurementsByUserID получает все измерения пользователя
func (r *MeasurementRepositoryImpl) GetMeasurementsByUserID(ctx context.Context, userID int) ([]*domain.MeasurementRead, error) {
	dbMeasurements, err := r.queries.GetMeasurementsByUser(ctx, int32(userID))
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(err, "GetMeasurementsByUserID", jsonData, "failed to query measurements")
		return nil, err
	}

	if len(dbMeasurements) == 0 {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Warn("GetMeasurementsByUserID", jsonData, "no measurements found")
		return []*domain.MeasurementRead{}, nil // Возвращаем пустой слайс вместо ошибки
	}

	measurements := make([]*domain.MeasurementRead, len(dbMeasurements))
	for i, m := range dbMeasurements {
		measurements[i] = &domain.MeasurementRead{
			MeasurementBase: domain.MeasurementBase{
				Type:  m.Type,
				Value: int(m.Value),
				Date:  m.Date,
			},
			ID: int(m.ID),
		}
	}

	jsonData := logging.MarshalLogData(map[string]interface{}{
		"user_id":        userID,
		"records_count":  len(measurements),
	})
	logging.Debug("GetMeasurementsByUserID", jsonData, "successfully retrieved measurements")

	return measurements, nil
}

// UpdateMeasurements обновляет все измерения пользователя (удаляет старые и создает новые)
func (r *MeasurementRepositoryImpl) UpdateMeasurements(ctx context.Context, userID int, measurements []*domain.MeasurementCreate) ([]*domain.MeasurementRead, error) {
	// Начинаем транзакцию
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(err, "UpdateMeasurements", jsonData, "failed to begin transaction")
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer func() {
		if err != nil {
			tx.Rollback()
		}
	}()

	// Создаем queries с транзакцией
	qtx := r.queries.WithTx(tx)

	// Удаляем все старые измерения пользователя
	err = qtx.DeleteMeasurementsByUser(ctx, int32(userID))
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(err, "UpdateMeasurements", jsonData, "failed to delete measurements")
		return nil, fmt.Errorf("failed to delete measurements: %w", err)
	}

	logging.Debug("UpdateMeasurements", 
		logging.MarshalLogData(map[string]interface{}{"user_id": userID}), 
		"deleted old measurements")

	// Создаем новые измерения
	createdMeasurements := make([]*domain.MeasurementRead, 0, len(measurements))
	for i, m := range measurements {
		params := gen.CreateMeasurementParams{
			UserID: int32(userID), // Используем переданный userID для безопасности
			Type:   m.Type,
			Value:  int32(m.Value),
			Date:   m.Date,
		}

		dbMeasurement, err := qtx.CreateMeasurement(ctx, params)
		if err != nil {
			jsonData := logging.MarshalLogData(map[string]interface{}{
				"user_id":   userID,
				"type":      m.Type,
				"index":     i,
			})
			logging.Error(err, "UpdateMeasurements", jsonData, "failed to create measurement")
			return nil, fmt.Errorf("failed to create measurement at index %d: %w", i, err)
		}

		createdMeasurements = append(createdMeasurements, &domain.MeasurementRead{
			MeasurementBase: domain.MeasurementBase{
				Type:  dbMeasurement.Type,
				Value: int(dbMeasurement.Value),
				Date:  dbMeasurement.Date,
			},
			ID: int(dbMeasurement.ID),
		})
	}

	// Коммитим транзакцию
	if err = tx.Commit(); err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(err, "UpdateMeasurements", jsonData, "failed to commit transaction")
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	jsonData := logging.MarshalLogData(map[string]interface{}{
		"user_id":       userID,
		"records_count": len(createdMeasurements),
	})
	logging.Debug("UpdateMeasurements", jsonData, "successfully updated measurements")

	return createdMeasurements, nil
}