package postgres

import (
	"github.com/lib/pq"
)

// GORM модели для базы данных
type (
	Exercise struct {
		ID    uint           `gorm:"primaryKey;column:id"`
		Title string         `gorm:"column:title;uniqueIndex;not null"`
		Tags  pq.StringArray `gorm:"column:tags;type:varchar[];not null"`
		Hrefs pq.StringArray `gorm:"column:hrefs;type:varchar[];not null"`
	}

	Training struct {
		ID                  uint                 `gorm:"primaryKey;column:id"`
		Title               string               `gorm:"column:title;not null"`
		PerfomableExercises []PerfomableExercise `gorm:"foreignKey:TrainingID"`
	}

	User struct {
		ID             uint   `gorm:"primaryKey;column:id"`
		Email          string `gorm:"column:email;uniqueIndex;not null"`
		Name           string `gorm:"column:name;not null"`
		HashedPassword string `gorm:"column:hashed_password;not null"`
	}

	Measurement struct {
		ID     uint   `gorm:"primaryKey;column:id"`
		UserID uint   `gorm:"column:user_id;index;not null"`
		Type   string `gorm:"column:type;not null"`
		Value  int    `gorm:"column:value;not null"`
		Date   string `gorm:"column:date;not null"`
		User   User   `gorm:"foreignKey:UserID"`
	}

	PerfomableExercise struct {
		ID         uint     `gorm:"primaryKey;column:id"`
		ExerciseID uint     `gorm:"column:exercise_id;not null"`
		TrainingID uint     `gorm:"column:training_id;not null"`
		Exercise   Exercise `gorm:"foreignKey:ExerciseID"`
		Training   Training `gorm:"foreignKey:TrainingID"`
		Sets       []Set    `gorm:"foreignKey:PerfomableExerciseID"`
	}

	Set struct {
		ID                   uint               `gorm:"primaryKey;column:id"`
		Weight               *int               `gorm:"column:weight"`
		Repetitions          *int               `gorm:"column:repetitions"`
		RestDuration         *int               `gorm:"column:rest_duration"`
		PerfomableExerciseID uint               `gorm:"column:perfomable_exercise_id;index;not null"`
		PerfomableExercise   PerfomableExercise `gorm:"foreignKey:PerfomableExerciseID"`
	}

	PlannedTraining struct {
		ID         uint           `gorm:"primaryKey;column:id"`
		UserID     uint           `gorm:"column:user_id;index;not null"`
		TrainingID uint           `gorm:"column:training_id;uniqueIndex;not null"`
		Weekdays   pq.StringArray `gorm:"column:weekdays;type:varchar[]"`
		User       User           `gorm:"foreignKey:UserID"`
		Training   Training       `gorm:"foreignKey:TrainingID"`
	}

	UserPerformedTraining struct {
		ID         uint     `gorm:"primaryKey;column:id"`
		UserID     uint     `gorm:"column:user_id;index;not null"`
		TrainingID uint     `gorm:"column:training_id;uniqueIndex;not null"`
		Date       string   `gorm:"column:date;not null"`
		User       User     `gorm:"foreignKey:UserID"`
		Training   Training `gorm:"foreignKey:TrainingID"`
	}
)

// TableName методы для явного указания имен таблиц
func (Exercise) TableName() string {
	return "exercises"
}

func (Training) TableName() string {
	return "trainings"
}

func (User) TableName() string {
	return "users"
}

func (Measurement) TableName() string {
	return "measurements"
}

func (PerfomableExercise) TableName() string {
	return "perfomable_exercises"
}

func (Set) TableName() string {
	return "sets"
}

func (PlannedTraining) TableName() string {
	return "planned_trainings"
}

func (UserPerformedTraining) TableName() string {
	return "user_performed_trainings"
}
