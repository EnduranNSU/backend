package domain

import (
	"context"
)

type MeasurementRepository interface {
	CreateMeasurement(ctx context.Context, measurement *MeasurementCreate) (*MeasurementRead, error)
	GetMeasurementsByUserID(ctx context.Context, userID int) ([]*MeasurementRead, error)
	UpdateMeasurements(ctx context.Context, userID int, measurements []*MeasurementCreate) ([]*MeasurementRead, error)
}