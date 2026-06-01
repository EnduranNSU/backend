package httpin

import (
	"net/http"
	"strings"

	"auth/internal/auth"
	"auth/internal/domain"
	"github.com/gin-gonic/gin"
)

type AuthMiddleware struct {
	jwtService  *auth.JWTService
	userService domain.UserRepository
}

func NewAuthMiddleware(jwtService *auth.JWTService, userService domain.UserRepository) *AuthMiddleware {
	return &AuthMiddleware{
		jwtService:  jwtService,
		userService: userService,
	}
}

func (m *AuthMiddleware) GetCurrentUser() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Получаем токен из заголовка Authorization
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "authorization header is required"})
			c.Abort()
			return
		}

		// Проверяем формат "Bearer <token>"
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid authorization header format"})
			c.Abort()
			return
		}

		tokenString := parts[1]

		// Валидируем токен и получаем email
		email, err := m.jwtService.ValidateToken(tokenString)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "invalid or expired token"})
			c.Abort()
			return
		}

		// Получаем пользователя по email
		user, err := m.userService.GetUser(c.Request.Context(), email)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get user"})
			c.Abort()
			return
		}

		if user == nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "user not found"})
			c.Abort()
			return
		}

		// Сохраняем пользователя в контексте
		c.Set("user", user)
		c.Next()
	}
}
