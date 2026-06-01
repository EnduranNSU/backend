package domain

import "time"

// MeasurementBase представляет базовые поля измерения
type MeasurementBase struct {
	Type  string `json:"type"`
	Value int    `json:"value"`
	Date  string `json:"date"`
}

// MeasurementRead представляет модель для чтения данных из БД
type MeasurementRead struct {
	MeasurementBase
	ID int `json:"id"`
}

// MeasurementCreate представляет модель для создания нового измерения
type MeasurementCreate struct {
	MeasurementBase
	UserID int `json:"user_id"`
}

// Опционально: если хотите работать с time.Time вместо строки для даты
type MeasurementBaseWithTime struct {
	Type  string    `json:"type"`
	Value int       `json:"value"`
	Date  time.Time `json:"date"`
}