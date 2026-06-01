package dto

// MeasurementBaseRequest базовый запрос для измерения
type MeasurementBaseRequest struct {
	Type  string `json:"type" binding:"required"`
	Value int    `json:"value" binding:"required,min=0"`
	Date  string `json:"date" binding:"required"`
}

// MeasurementResponse ответ с данными измерения
type MeasurementResponse struct {
	ID    int    `json:"id"`
	Type  string `json:"type"`
	Value int    `json:"value"`
	Date  string `json:"date"`
}

// UpdateMeasurementsRequest запрос на обновление измерений
type UpdateMeasurementsRequest []MeasurementBaseRequest