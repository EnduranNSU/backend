// @title Enduran User Info API
// @version 1.0
// @description Сервис информации о пользователе (вес, рост, возраст и т.д.)
// @BasePath /api/v1

package httpin

import (
	"github.com/gin-gonic/gin"

	_ "github.com/EnduranNSU/end-user-info/docs"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// NewGinRouter создает новый Gin router для измерений
// @title Enduran User Info API
// @version 1.0
// @description Сервис информации о пользователе (вес, рост, возраст и т.д.)
// @BasePath /api/v1
func NewGinRouter(h *MeasurementHandler, authBaseURL string) *gin.Engine {
	r := gin.New()
	r.Use(gin.Logger(), gin.Recovery())

	r.StaticFile("/openapi.yaml", "docs/swagger.yaml")

	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	authMW := NewAuthMiddleware(authBaseURL)

	api := r.Group("/api/v1")
	api.Use(authMW.Handle)
	{
		// Роуты для измерений
		api.GET("/measurements", h.GetMeasurements)
		api.POST("/measurements/create", h.CreateMeasurement)
		api.POST("/measurements/update", h.UpdateMeasurements)
	}

	return r
}