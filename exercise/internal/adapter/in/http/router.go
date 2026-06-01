// @title Exercise API
// @version 1.0
// @description Сервис информации о упражнениях
// @BasePath /api/v1
package httpin

import (
	"github.com/gin-gonic/gin"

	_ "github.com/EnduranNSU/exercise/docs"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// NewGinRouter создает новый Gin router
// @title Enduran Exercise API
// @version 1.0
// @description Сервис информации о упражнениях
// @BasePath /api/v1
func NewGinRouter(exerciseHandler *ExerciseHandler, authBaseURL string) *gin.Engine {
	r := gin.New()
	r.Use(gin.Logger(), gin.Recovery())

	// Статические файлы для Swagger
	r.StaticFile("/openapi.yaml", "docs/swagger.yaml")
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// API группа с аутентификацией - ВАЖНО: используем /api/v1
	api := r.Group("/api/v1")
	// Создаем middleware с URL auth сервиса
	authMW := NewAuthMiddleware(authBaseURL)
	api.Use(authMW.Handle)

	// Регистрируем маршруты упражнений в группе api
	exerciseGroup := api.Group("/exercise") // <- Используем api, а не r
	{
		exerciseGroup.GET("", exerciseHandler.GetExercises)
		exerciseGroup.GET("/:id", exerciseHandler.GetExerciseById)
	}

	return r
}
