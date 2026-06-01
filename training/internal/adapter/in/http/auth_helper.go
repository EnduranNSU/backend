package httpin

import (
	"net/http"

	"github.com/EnduranNSU/trainings/internal/adapter/in/http/dto"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// helper: достаём userID, который положил AuthMiddleware
func userIDFromContext(c *gin.Context) (uuid.UUID, bool) {
	v, ok := c.Get("userID")
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "unauthorized"})
		return uuid.Nil, false
	}

	s, ok := v.(string)
	if !ok {
		c.AbortWithStatusJSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "unauthorized"})
		return uuid.Nil, false
	}

	id, err := uuid.Parse(s)
	if err != nil {
		c.AbortWithStatusJSON(http.StatusUnauthorized, dto.ErrorResponse{Error: "unauthorized"})
		return uuid.Nil, false
	}

	return id, true
}
