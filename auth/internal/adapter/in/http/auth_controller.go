package httpin

import (
	"net/http"

	"auth/internal/auth"
	"auth/internal/domain"
	"auth/internal/service"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
)

type AuthController struct {
	authService *service.AuthService
}

func NewAuthController(authService *service.AuthService) *AuthController {
	return &AuthController{
		authService: authService,
	}
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

// Login godoc
// @Summary Login user
// @Description Authenticate user and return access token
// @Tags auth
// @Accept json
// @Produce json
// @Param request body LoginRequest true "Login credentials"
// @Success 200 {object} auth.Token
// @Failure 400 {object} map[string]interface{}
// @Failure 401 {object} map[string]interface{}
// @Router /api/v1/login [post]
func (c *AuthController) Login(ctx *gin.Context) {
	var req LoginRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	log.Info().Msgf("Login attempt for user: %s", req.Username)

	// Аутентификация пользователя
	user, err := c.authService.AuthenticateUser(ctx.Request.Context(), req.Username, req.Password)
	if err != nil {
		log.Error().Err(err).Msg("Authentication failed")
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "internal server error"})
		return
	}

	if user == nil {
		log.Warn().Msgf("Authentication failed for user: %s", req.Username)
		ctx.JSON(http.StatusUnauthorized, gin.H{"error": "Incorrect username or password"})
		return
	}

	log.Info().Msgf("User authenticated successfully: %s", user.Email)

	// Создаем access token
	accessToken, err := c.authService.CreateAccessToken(user.Email)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create token")
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create token"})
		return
	}

	log.Info().Msgf("Token created for user: %s, token: %s...", user.Email, accessToken[:50])

	ctx.JSON(http.StatusOK, auth.NewToken(accessToken))
}

// ValidateResponse структура ответа для валидации
type ValidateResponse struct {
	Valid bool     `json:"valid"`
	User  UserInfo `json:"user"`
}

type UserInfo struct {
	ID    int    `json:"id"`
	Email string `json:"email"`
	Name  string `json:"name"`
}

// Validate godoc
// @Summary Validate token
// @Description Check if access token is valid and return user info
// @Tags auth
// @Accept json
// @Produce json
// @Security BearerAuth
// @Success 200 {object} ValidateResponse
// @Failure 401 {object} map[string]interface{}
// @Router /api/v1/validate [get]
func (c *AuthController) Validate(ctx *gin.Context) {
	// Получаем пользователя из контекста (установлен middleware)
	userInterface, exists := ctx.Get("user")
	if !exists {
		ctx.JSON(http.StatusUnauthorized, gin.H{
			"valid": false,
			"error": "user not found",
		})
		return
	}

	user, ok := userInterface.(*domain.UserRead)
	if !ok {
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"valid": false,
			"error": "invalid user type",
		})
		return
	}

	// Возвращаем успешный ответ с информацией о пользователе
	ctx.JSON(http.StatusOK, ValidateResponse{
		Valid: true,
		User: UserInfo{
			ID:    user.ID,
			Email: user.Email,
			Name:  user.Name,
		},
	})
}
