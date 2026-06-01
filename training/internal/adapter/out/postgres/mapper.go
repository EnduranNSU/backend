package postgres

import "github.com/EnduranNSU/trainings/internal/domain"

func (r *trainingRepositoryGorm) toDomainPlannedTraining(pt *PlannedTraining) *domain.PlannedTraining {
	if pt == nil {
		return nil
	}

	return &domain.PlannedTraining{
		ID:       int(pt.ID),
		UserID:   int(pt.UserID),
		Weekdays: pt.Weekdays,
		Training: r.toDomainTraining(&pt.Training),
	}
}

func (r *trainingRepositoryGorm) toDomainPerformedTraining(pt *UserPerformedTraining) *domain.UserPerformedTraining {
	if pt == nil {
		return nil
	}

	return &domain.UserPerformedTraining{
		ID:       int(pt.ID),
		UserID:   int(pt.UserID),
		Date:     pt.Date,
		Training: r.toDomainTraining(&pt.Training),
	}
}

func (r *trainingRepositoryGorm) toDomainTraining(t *Training) *domain.Training {
	if t == nil {
		return nil
	}

	perfExercises := make([]domain.PerfomableExercise, len(t.PerfomableExercises))
	for i, pe := range t.PerfomableExercises {
		sets := make([]domain.Set, len(pe.Sets))
		for j, s := range pe.Sets {
			sets[j] = domain.Set{
				Weight:       s.Weight,
				Repetitions:  s.Repetitions,
				RestDuration: s.RestDuration,
			}
		}

		perfExercises[i] = domain.PerfomableExercise{
			ExerciseID: int(pe.ExerciseID),
			Sets:       sets,
		}
	}

	return &domain.Training{
		Title:               t.Title,
		PerfomableExercises: perfExercises,
	}
}
