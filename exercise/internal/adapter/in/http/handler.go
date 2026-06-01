package httpin

import (
	"net/http"
	"strconv"

	"github.com/EnduranNSU/exercise/internal/adapter/in/http/dto"
	"github.com/EnduranNSU/exercise/internal/domain"
	"github.com/gin-gonic/gin"
)

// Вспомогательные функции для получения данных пользователя из контекста
func getUserID(c *gin.Context) (int, bool) {
	userID, exists := c.Get("userID")
	if !exists {
		return 0, false
	}
	id, ok := userID.(int)
	return id, ok
}

type ExerciseHandler struct {
	repo domain.ExerciseRepository
}

func NewTrainingHandler(repo domain.ExerciseRepository) *ExerciseHandler {
	return &ExerciseHandler{
		repo: repo,
	}
}

// GetExercises возвращает список всех упражнений
// @Summary Get all exercises
// @Tags exercise
// @Produce json
// @Success 200 {array} domain.ExerciseRead
// @Failure 500 {object} map[string]interface{}
// @Router /exercise [get]
func (h *ExerciseHandler) GetExercises(c *gin.Context) {
	// Получаем ID пользователя из контекста
	userID, ok := getUserID(c)
	if !ok {
		c.JSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "User not authenticated"})
		return
	}

	// Можно использовать userID для фильтрации, если нужно
	_ = userID

	exercises, err := h.repo.GetExercises(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError,
			dto.ErrorResponse{Error: "Failed to get exercises"},
		)
		return
	}

	c.JSON(http.StatusOK, exercises)
}

// GetExerciseById возвращает упражнение по ID с описанием
// @Summary Get exercise by ID
// @Tags exercise
// @Produce json
// @Param id path int true "Exercise ID"
// @Success 200 {object} domain.ExerciseReadVerbose
// @Failure 404 {object} map[string]interface{}
// @Failure 500 {object} map[string]interface{}
// @Router /exercise/{id} [get]
func (h *ExerciseHandler) GetExerciseById(c *gin.Context) {
	// Получаем ID пользователя из контекста
	userID, ok := getUserID(c)
	if !ok {
		c.JSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "User not authenticated"})
		return
	}

	// Можно использовать userID для проверки прав доступа
	_ = userID

	idStr := c.Param("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest,
			dto.ErrorResponse{Error: "Invalid exercise ID format"},
		)
		return
	}

	exercise, err := h.repo.GetExerciseById(c.Request.Context(), id)
	if err != nil {
		c.JSON(http.StatusInternalServerError,
			dto.ErrorResponse{Error: "Failed to get exercise"},
		)
		return
	}

	if exercise == nil {
		c.JSON(http.StatusNotFound,
			dto.ErrorResponse{Error: "Exercise not found"},
		)
		return
	}

	c.JSON(http.StatusOK, exercise)
}
