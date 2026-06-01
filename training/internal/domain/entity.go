package domain

import (
	"github.com/lib/pq"
)

// Set - подход (сет) в упражнении
type Set struct {
	ID                   int  `json:"id"`
	Weight               *int `json:"weight,omitempty"`        // указатель для nullable поля
	Repetitions          *int `json:"repetitions,omitempty"`   // указатель для nullable поля
	RestDuration         *int `json:"rest_duration,omitempty"` // указатель для nullable поля
	PerfomableExerciseID int  `json:"perfomable_exercise_id"`
}

// Exercise - базовое упражнение
type Exercise struct {
	ID          int            `json:"id"`
	Title       string         `json:"title"`
	Tags        pq.StringArray `json:"tags"`
	Hrefs       pq.StringArray `json:"hrefs"`
	Description *string        `json:"description,omitempty"` // указатель для nullable поля
}

// PerfomableExercise - выполняемое упражнение (связь тренировки и упражнения)
type PerfomableExercise struct {
	ID         int       `json:"id"`
	ExerciseID int       `json:"exercise_id"`
	TrainingID int       `json:"training_id"`
	Exercise   *Exercise `json:"exercise,omitempty"`
	Sets       []Set     `json:"sets"`
}

// Training - тренировка
type Training struct {
	ID                  int                  `json:"id"`
	Title               string               `json:"title"`
	PerfomableExercises []PerfomableExercise `json:"perfomable_exercises"`
}

// PlannedTraining - запланированная тренировка
type PlannedTraining struct {
	ID         int            `json:"id"`
	UserID     int            `json:"user_id"`
	TrainingID int            `json:"training_id"`
	Weekdays   pq.StringArray `json:"weekdays"`
	Training   *Training      `json:"training"`
}

// UserPerformedTraining - выполненная тренировка пользователя
type UserPerformedTraining struct {
	ID         int       `json:"id"`
	UserID     int       `json:"user_id"`
	TrainingID int       `json:"training_id"`
	Date       string    `json:"date"`
	Training   *Training `json:"training"`
}

// ========== Параметры для создания запланированной тренировки ==========

// CreatePlannedTrainingParams - параметры для создания запланированной тренировки
type CreatePlannedTrainingParams struct {
	UserID   int                  `json:"user_id"`
	Weekdays []string             `json:"weekdays"`
	Training TrainingCreateParams `json:"training"`
}

// ========== Параметры для создания выполненной тренировки ==========

// CreateUserPerformedTrainingParams - параметры для создания выполненной тренировки
type CreateUserPerformedTrainingParams struct {
	UserID   int                  `json:"user_id"`
	Date     string               `json:"date"`
	Training TrainingCreateParams `json:"training"`
}

// ========== Вложенные параметры ==========

// TrainingCreateParams - параметры для создания тренировки
type TrainingCreateParams struct {
	Title               string                           `json:"title"`
	PerfomableExercises []PerfomableExerciseCreateParams `json:"perfomable_exercises"`
}

// PerfomableExerciseCreateParams - параметры для создания выполняемого упражнения
type PerfomableExerciseCreateParams struct {
	ExerciseID int               `json:"exercise_id"`
	Sets       []SetCreateParams `json:"sets"`
}

// SetCreateParams - параметры для создания сета
type SetCreateParams struct {
	Weight       *int `json:"weight,omitempty"`
	Repetitions  *int `json:"repetitions,omitempty"`
	RestDuration *int `json:"rest_duration,omitempty"`
}
