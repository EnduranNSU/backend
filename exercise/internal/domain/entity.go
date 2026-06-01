package domain

import (
	"github.com/lib/pq"
)

// ExerciseBase contains the common fields for all exercise models
type ExerciseBase struct {
	Title string         `json:"title"`
	Tags  pq.StringArray `json:"tags"`
	Hrefs pq.StringArray `json:"hrefs"`
}

// ExerciseRead represents the basic exercise read model
type ExerciseRead struct {
	ID    int            `json:"id"`
	Title string         `json:"title"`
	Tags  pq.StringArray `json:"tags"`
	Hrefs pq.StringArray `json:"hrefs"`
}

// ExerciseReadVerbose represents the detailed exercise read model with description
type ExerciseReadVerbose struct {
	ID          int            `json:"id"`
	Title       string         `json:"title"`
	Tags        pq.StringArray `json:"tags"`
	Hrefs       pq.StringArray `json:"hrefs"`
	Description string         `json:"description"`
}

// ExerciseCreate represents the model for creating a new exercise
type ExerciseCreate struct {
	Title       string         `json:"title"`
	Tags        pq.StringArray `json:"tags"`
	Hrefs       pq.StringArray `json:"hrefs"`
	Description string         `json:"description"`
}
