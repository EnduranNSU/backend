package httpin

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/EnduranNSU/end-user-info/internal/adapter/in/http/dto"
	"github.com/EnduranNSU/end-user-info/internal/domain"
	"github.com/EnduranNSU/end-user-info/internal/logging"
)

type MeasurementHandler struct {
	repo domain.MeasurementRepository
}

func NewMeasurementHandler(repo domain.MeasurementRepository) *MeasurementHandler {
	return &MeasurementHandler{repo: repo}
}

// helper: достаём userID из контекста
func userIDFromContext(c *gin.Context) (int, bool) {
	v, ok := c.Get("userID")
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "unauthorized"})
		return 0, false
	}

	// Предполагаем, что userID хранится как int или float64
	var userID int
	switch val := v.(type) {
	case int:
		userID = val
	case float64:
		userID = int(val)
	case int64:
		userID = int(val)
	default:
		c.AbortWithStatusJSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "invalid user id type"})
		return 0, false
	}

	return userID, true
}

// GetMeasurements получает все измерения пользователя
// @Summary      Получить все измерения
// @Description  Возвращает все измерения пользователя
// @Tags         measurements
// @Produce      json
// @Param        Authorization  header    string  true  "Bearer access токен"
// @Success      200  {array}   dto.MeasurementResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Security     BearerAuth
// @Router       /measurements [get]
func (h *MeasurementHandler) GetMeasurements(c *gin.Context) {
	userID, ok := userIDFromContext(c)
	if !ok {
		return
	}

	measurements, err := h.repo.GetMeasurementsByUserID(c.Request.Context(), userID)
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(err, "GetMeasurements", jsonData, "failed to get measurements")
		c.AbortWithStatusJSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to get measurements"})
		return
	}

	resp := make([]dto.MeasurementResponse, 0, len(measurements))
	for _, m := range measurements {
		resp = append(resp, dto.MeasurementResponse{
			ID:    m.ID,
			Type:  m.Type,
			Value: m.Value,
			Date:  m.Date,
		})
	}

	jsonData := logging.MarshalLogData(map[string]interface{}{
		"user_id":       userID,
		"records_count": len(resp),
	})
	logging.Debug("GetMeasurements", jsonData, "successfully retrieved measurements")

	c.JSON(http.StatusOK, resp)
}

// CreateMeasurement создает новое измерение
// @Summary      Создать измерение
// @Description  Создает новое измерение для пользователя
// @Tags         measurements
// @Accept       json
// @Produce      json
// @Param        Authorization  header    string                       true  "Bearer access токен"
// @Param        request        body      dto.MeasurementBaseRequest   true  "Данные измерения"
// @Success      200  {object}  dto.MeasurementResponse
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Security     BearerAuth
// @Router       /measurements/create [post]
func (h *MeasurementHandler) CreateMeasurement(c *gin.Context) {
	userID, ok := userIDFromContext(c)
	if !ok {
		return
	}

	var req dto.MeasurementBaseRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
			"error":   err.Error(),
		})
		logging.Warn("CreateMeasurement", jsonData, "invalid request body")
		c.AbortWithStatusJSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid request body"})
		return
	}

	measurementCreate := &domain.MeasurementCreate{
		MeasurementBase: domain.MeasurementBase{
			Type:  req.Type,
			Value: req.Value,
			Date:  req.Date,
		},
		UserID: userID,
	}

	result, err := h.repo.CreateMeasurement(c.Request.Context(), measurementCreate)
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
			"type":    req.Type,
			"value":   req.Value,
			"date":    req.Date,
		})
		logging.Error(err, "CreateMeasurement", jsonData, "failed to create measurement")
		c.AbortWithStatusJSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to create measurement"})
		return
	}

	if result == nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(nil, "CreateMeasurement", jsonData, "unexpected nil result")
		c.AbortWithStatusJSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "internal server error"})
		return
	}

	jsonData := logging.MarshalLogData(map[string]interface{}{
		"user_id":       userID,
		"measurement_id": result.ID,
	})
	logging.Debug("CreateMeasurement", jsonData, "successfully created measurement")

	c.JSON(http.StatusOK, dto.MeasurementResponse{
		ID:    result.ID,
		Type:  result.Type,
		Value: result.Value,
		Date:  result.Date,
	})
}

// UpdateMeasurements обновляет все измерения пользователя
// @Summary      Обновить все измерения
// @Description  Удаляет все старые измерения и создает новые
// @Tags         measurements
// @Accept       json
// @Produce      json
// @Param        Authorization  header    string                         true  "Bearer access токен"
// @Param        request        body      dto.UpdateMeasurementsRequest  true  "Массив измерений"
// @Success      200  {array}   dto.MeasurementResponse
// @Failure      400  {object}  dto.ErrorResponse
// @Failure      401  {object}  dto.ErrorResponse
// @Failure      500  {object}  dto.ErrorResponse
// @Security     BearerAuth
// @Router       /measurements/update [post]
func (h *MeasurementHandler) UpdateMeasurements(c *gin.Context) {
	userID, ok := userIDFromContext(c)
	if !ok {
		return
	}

	var req dto.UpdateMeasurementsRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
			"error":   err.Error(),
		})
		logging.Warn("UpdateMeasurements", jsonData, "invalid request body")
		c.AbortWithStatusJSON(http.StatusBadRequest, dto.ErrorResponse{Error: "invalid request body"})
		return
	}

	// Преобразуем запрос в domain модели
	measurementsCreate := make([]*domain.MeasurementCreate, 0, len(req))
	for _, m := range req {
		measurementsCreate = append(measurementsCreate, &domain.MeasurementCreate{
			MeasurementBase: domain.MeasurementBase{
				Type:  m.Type,
				Value: m.Value,
				Date:  m.Date,
			},
			UserID: userID,
		})
	}

	results, err := h.repo.UpdateMeasurements(c.Request.Context(), userID, measurementsCreate)
	if err != nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id":       userID,
			"records_count": len(req),
		})
		logging.Error(err, "UpdateMeasurements", jsonData, "failed to update measurements")
		c.AbortWithStatusJSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "failed to update measurements"})
		return
	}

	if results == nil {
		jsonData := logging.MarshalLogData(map[string]interface{}{
			"user_id": userID,
		})
		logging.Error(nil, "UpdateMeasurements", jsonData, "unexpected nil result")
		c.AbortWithStatusJSON(http.StatusInternalServerError, dto.ErrorResponse{Error: "internal server error"})
		return
	}

	resp := make([]dto.MeasurementResponse, 0, len(results))
	for _, m := range results {
		resp = append(resp, dto.MeasurementResponse{
			ID:    m.ID,
			Type:  m.Type,
			Value: m.Value,
			Date:  m.Date,
		})
	}

	jsonData := logging.MarshalLogData(map[string]interface{}{
		"user_id":       userID,
		"records_count": len(resp),
	})
	logging.Debug("UpdateMeasurements", jsonData, "successfully updated measurements")

	c.JSON(http.StatusOK, resp)
}