package httpin

import (
	"net/http"

	"auth/internal/auth"
	"auth/internal/domain"
	"github.com/gin-gonic/gin"
)

type SignupController struct {
	userService domain.UserRepository
}

func NewSignupController(userService domain.UserRepository) *SignupController {
	return &SignupController{
		userService: userService,
	}
}

// Signup godoc
// @Summary Register new user
// @Description Create a new user account
// @Tags auth
// @Accept json
// @Produce json
// @Param request body domain.UserCreate true "User registration data"
// @Success 201 {object} domain.UserRead
// @Failure 400 {object} map[string]interface{}
// @Failure 409 {object} map[string]interface{}
// @Router /api/v1/register [post]
func (c *SignupController) Signup(ctx *gin.Context) {
	var req domain.UserCreate
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Создаем пользователя
	hashedPassword, _ := auth.Hash(req.Password)
	user, err := c.userService.CreateUser(ctx.Request.Context(), req, hashedPassword)
	if err != nil {
		// Проверяем, возможно пользователь уже существует
		// В реальном приложении нужно парсить ошибку БД о нарушении уникальности
		ctx.JSON(http.StatusBadRequest, gin.H{
			"error":  "User already exists",
			"detail": "User with this email already exists",
		})
		return
	}

	ctx.JSON(http.StatusCreated, user)
}
