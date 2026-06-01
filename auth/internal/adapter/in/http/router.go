// @title Training API
// @version 1.0
// @description Сервис авторизации
// @BasePath /api/v1
package httpin

import (
	_ "auth/docs"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// RouterConfig содержит все зависимости для роутера
type RouterConfig struct {
	AuthController   *AuthController
	SignupController *SignupController
	UserController   *UserController
	AuthMiddleware   *AuthMiddleware
}

// NewGinRouter создает новый Gin router
// @title Enduran Training API
// @version 1.0
// @description Сервис авторизации
// @BasePath /api/v1
func NewGinRouter(cfg *RouterConfig) *gin.Engine {
	r := gin.New()
	r.Use(gin.Recovery())

	// Swagger документация
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// API v1 группа
	api := r.Group("/api/v1")
	{
		// Публичные эндпоинты
		api.POST("/register", cfg.SignupController.Signup)
		api.POST("/login", cfg.AuthController.Login)

		// Эндпоинт для валидации токена (требует аутентификации)
		// ВАЖНО: этот эндпоинт должен быть ЗА middleware
		validate := api.Group("/")
		validate.Use(cfg.AuthMiddleware.GetCurrentUser())
		{
			validate.GET("/validate", cfg.AuthController.Validate)
		}

		// Защищенные эндпоинты
		protected := api.Group("/")
		protected.Use(cfg.AuthMiddleware.GetCurrentUser())
		{
			protected.GET("/user", cfg.UserController.GetCurrentUser)
		}
	}

	return r
}
