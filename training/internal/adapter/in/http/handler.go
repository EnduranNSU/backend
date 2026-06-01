package httpin

import (
	"net/http"
	"strconv"

	"github.com/EnduranNSU/trainings/internal/adapter/in/http/dto"
	"github.com/EnduranNSU/trainings/internal/domain"
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

type TrainingHandler struct {
	repo domain.TrainingRepository
}

func NewTrainingHandler(repo domain.TrainingRepository) *TrainingHandler {
	return &TrainingHandler{
		repo: repo,
	}
}

// ========== Planned Trainings ==========

// GetPlannedTrainings возвращает все запланированные тренировки пользователя
// @Summary      Получить запланированные тренировки
// @Description  Возвращает все запланированные тренировки текущего пользователя
// @Tags         planned-trainings
// @Produce      json
// @Success      200  {array}   domain.PlannedTraining
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/planned [get]
func (h *TrainingHandler) GetPlannedTrainings(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	trainings, err := h.repo.GetPlannedTrainings(c.Request.Context(), int(userID))
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get planned trainings"})
		return
	}

	c.JSON(http.StatusOK, trainings)
}

// GetPlannedTraining возвращает запланированную тренировку по ID
// @Summary      Получить запланированную тренировку
// @Description  Возвращает запланированную тренировку по её ID
// @Tags         planned-trainings
// @Produce      json
// @Param        id   path      int  true  "Training ID"
// @Success      200  {object}  domain.PlannedTraining
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      404  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/planned/{id} [get]
func (h *TrainingHandler) GetPlannedTraining(c *gin.Context) {
	trainingID, err := parseIntParam(c, "id")
	if err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid training id"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	training, err := h.repo.GetPlannedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get planned training"})
		return
	}

	if training == nil {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Planned training not found"})
		return
	}

	// Проверяем, что тренировка принадлежит пользователю
	if training.UserID != int(userID) {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Planned training not found"})
		return
	}

	c.JSON(http.StatusOK, training)
}

// CreatePlannedTraining создает новую запланированную тренировку
// @Summary      Создать запланированную тренировку
// @Description  Создает новую запланированную тренировку для текущего пользователя
// @Tags         planned-trainings
// @Accept       json
// @Produce      json
// @Param        request body CreatePlannedTrainingRequest true "Данные тренировки"
// @Success      201  {object}  domain.PlannedTraining
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/planned/create [post]
func (h *TrainingHandler) CreatePlannedTraining(c *gin.Context) {
	var req CreatePlannedTrainingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "bad json"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	params := domain.CreatePlannedTrainingParams{
		UserID:   int(userID),
		Weekdays: req.Weekdays,
		Training: req.Training,
	}

	training, err := h.repo.CreatePlannedTraining(c.Request.Context(), params)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to create planned training"})
		return
	}

	if training == nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "It should not happen. Ask developer what is going on"})
		return
	}

	c.JSON(http.StatusCreated, training)
}

// DeletePlannedTraining удаляет запланированную тренировку
// @Summary      Удалить запланированную тренировку
// @Description  Удаляет запланированную тренировку по ID
// @Tags         planned-trainings
// @Produce      json
// @Param        id   path      int  true  "Training ID"
// @Success      204
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/planned/delete/{id} [post]
func (h *TrainingHandler) DeletePlannedTraining(c *gin.Context) {
	trainingID, err := parseIntParam(c, "id")
	if err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid training id"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	// Проверяем, что тренировка принадлежит пользователю
	training, err := h.repo.GetPlannedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get planned training"})
		return
	}

	if training == nil || training.UserID != int(userID) {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Planned training not found"})
		return
	}

	err = h.repo.DeletePlannedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to delete planned training"})
		return
	}

	c.Status(http.StatusNoContent)
}

// UpdatePlannedTraining обновляет запланированную тренировку
// @Summary      Обновить запланированную тренировку
// @Description  Обновляет запланированную тренировку по ID
// @Tags         planned-trainings
// @Accept       json
// @Produce      json
// @Param        id   path      int  true  "Training ID"
// @Param        request body CreatePlannedTrainingRequest true "Данные тренировки"
// @Success      200  {object}  domain.PlannedTraining
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      404  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/planned/update/{id} [post]
func (h *TrainingHandler) UpdatePlannedTraining(c *gin.Context) {
	trainingID, err := parseIntParam(c, "id")
	if err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid training id"})
		return
	}

	var req CreatePlannedTrainingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "bad json"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	// Проверяем существование тренировки
	existing, err := h.repo.GetPlannedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get planned training"})
		return
	}

	if existing == nil || existing.UserID != int(userID) {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Planned training not found"})
		return
	}

	params := domain.CreatePlannedTrainingParams{
		UserID:   int(userID),
		Weekdays: req.Weekdays,
		Training: req.Training,
	}

	training, err := h.repo.UpdatePlannedTraining(c.Request.Context(), trainingID, params)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to update planned training"})
		return
	}

	if training == nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "It should not happen. Ask developer what is going on"})
		return
	}

	c.JSON(http.StatusOK, training)
}

// ========== User Performed Trainings ==========

// GetUserPerformedTrainings возвращает все выполненные тренировки пользователя
// @Summary      Получить выполненные тренировки
// @Description  Возвращает все выполненные тренировки текущего пользователя
// @Tags         performed-trainings
// @Produce      json
// @Success      200  {array}   domain.UserPerformedTraining
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/user_performed [get]
func (h *TrainingHandler) GetUserPerformedTrainings(c *gin.Context) {
	userID, ok := getUserID(c)
	if !ok {
		return
	}

	trainings, err := h.repo.GetUserPerformedTrainings(c.Request.Context(), int(userID))
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get performed trainings"})
		return
	}

	c.JSON(http.StatusOK, trainings)
}

// GetUserPerformedTraining возвращает выполненную тренировку по ID
// @Summary      Получить выполненную тренировку
// @Description  Возвращает выполненную тренировку по её ID
// @Tags         performed-trainings
// @Produce      json
// @Param        id   path      int  true  "Training ID"
// @Success      200  {object}  domain.UserPerformedTraining
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      404  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/user_performed/{id} [get]
func (h *TrainingHandler) GetUserPerformedTraining(c *gin.Context) {
	trainingID, err := parseIntParam(c, "id")
	if err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid training id"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	training, err := h.repo.GetUserPerformedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get performed training"})
		return
	}

	if training == nil {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Performed training not found"})
		return
	}

	// Проверяем, что тренировка принадлежит пользователю
	if training.UserID != int(userID) {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Performed training not found"})
		return
	}

	c.JSON(http.StatusOK, training)
}

// CreateUserPerformedTraining создает новую выполненную тренировку
// @Summary      Создать выполненную тренировку
// @Description  Создает новую выполненную тренировку для текущего пользователя
// @Tags         performed-trainings
// @Accept       json
// @Produce      json
// @Param        request body CreateUserPerformedTrainingRequest true "Данные тренировки"
// @Success      201  {object}  domain.UserPerformedTraining
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/user_performed/create [post]
func (h *TrainingHandler) CreateUserPerformedTraining(c *gin.Context) {
	var req CreateUserPerformedTrainingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "bad json"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	params := domain.CreateUserPerformedTrainingParams{
		UserID:   int(userID),
		Date:     req.Date,
		Training: req.Training,
	}

	training, err := h.repo.CreateUserPerformedTraining(c.Request.Context(), params)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to create performed training"})
		return
	}

	if training == nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "It should not happen. Ask developer what is going on"})
		return
	}

	c.JSON(http.StatusCreated, training)
}

// DeleteUserPerformedTraining удаляет выполненную тренировку
// @Summary      Удалить выполненную тренировку
// @Description  Удаляет выполненную тренировку по ID
// @Tags         performed-trainings
// @Produce      json
// @Param        id   path      int  true  "Training ID"
// @Success      204
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/user_performed/delete/{id} [post]
func (h *TrainingHandler) DeleteUserPerformedTraining(c *gin.Context) {
	trainingID, err := parseIntParam(c, "id")
	if err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid training id"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	// Проверяем, что тренировка принадлежит пользователю
	training, err := h.repo.GetUserPerformedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get performed training"})
		return
	}

	if training == nil || training.UserID != int(userID) {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Performed training not found"})
		return
	}

	err = h.repo.DeleteUserPerformedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to delete performed training"})
		return
	}

	c.Status(http.StatusNoContent)
}

// UpdateUserPerformedTraining обновляет выполненную тренировку
// @Summary      Обновить выполненную тренировку
// @Description  Обновляет выполненную тренировку по ID
// @Tags         performed-trainings
// @Accept       json
// @Produce      json
// @Param        id   path      int  true  "Training ID"
// @Param        request body CreateUserPerformedTrainingRequest true "Данные тренировки"
// @Success      200  {object}  domain.UserPerformedTraining
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      404  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Router       /training/user_performed/update/{id} [post]
func (h *TrainingHandler) UpdateUserPerformedTraining(c *gin.Context) {
	trainingID, err := parseIntParam(c, "id")
	if err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid training id"})
		return
	}

	var req CreateUserPerformedTrainingRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, dto.ErrorResponse{Error: "bad json"})
		return
	}

	userID, ok := getUserID(c)
	if !ok {
		return
	}

	// Проверяем существование тренировки
	existing, err := h.repo.GetUserPerformedTraining(c.Request.Context(), trainingID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get performed training"})
		return
	}

	if existing == nil || existing.UserID != int(userID) {
		c.JSON(http.StatusNotFound, dto.ErrorResponse{Error: "Performed training not found"})
		return
	}

	params := domain.CreateUserPerformedTrainingParams{
		UserID:   int(userID),
		Date:     req.Date,
		Training: req.Training,
	}

	training, err := h.repo.UpdateUserPerformedTraining(c.Request.Context(), trainingID, params)
	if err != nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to update performed training"})
		return
	}

	if training == nil {
		c.JSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "It should not happen. Ask developer what is going on"})
		return
	}

	c.JSON(http.StatusOK, training)
}

// ========== Request Structs ==========

// CreatePlannedTrainingRequest представляет запрос на создание запланированной тренировки
type CreatePlannedTrainingRequest struct {
	Weekdays []string                    `json:"weekdays" binding:"required"`
	Training domain.TrainingCreateParams `json:"training" binding:"required"`
}

// CreateUserPerformedTrainingRequest представляет запрос на создание выполненной тренировки
type CreateUserPerformedTrainingRequest struct {
	Date     string                      `json:"date" binding:"required"`
	Training domain.TrainingCreateParams `json:"training" binding:"required"`
}

// ========== Helper Functions ==========

func parseIntParam(c *gin.Context, param string) (int, error) {
	value := c.Param(param)
	if value == "" {
		return 0, nil
	}

	id, err := strconv.Atoi(value)
	if err != nil {
		return 0, err
	}

	return id, nil
}
