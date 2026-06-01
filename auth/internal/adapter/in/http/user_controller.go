package httpin

import (
	"net/http"

	"auth/internal/domain"
	"github.com/gin-gonic/gin"
)

type UserController struct{}

func NewUserController() *UserController {
	return &UserController{}
}

// GetCurrentUser godoc
// @Summary Get current user
// @Description Get authenticated user information
// @Tags user
// @Accept json
// @Produce json
// @Security BearerAuth
// @Success 200 {object} domain.UserRead
// @Failure 401 {object} map[string]interface{}
// @Router /api/v1/user [get]
func (c *UserController) GetCurrentUser(ctx *gin.Context) {
	userInterface, exists := ctx.Get("user")
	if !exists {
		ctx.JSON(http.StatusUnauthorized, gin.H{"error": "user not found in context"})
		return
	}

	user, ok := userInterface.(*domain.UserRead)
	if !ok {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "invalid user type in context"})
		return
	}

	ctx.JSON(http.StatusOK, user)
}
