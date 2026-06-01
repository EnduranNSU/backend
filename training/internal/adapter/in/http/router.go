// @title Training API
// @version 1.0
// @description Сервис информации о тренировках и упражнения
// @BasePath /api/v1
package httpin

import (
	"github.com/gin-gonic/gin"

	_ "github.com/EnduranNSU/trainings/docs"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

// NewGinRouter создает новый Gin router
// @title Enduran Training API
// @version 1.0
// @description Сервис информации о тренировках и упражнения
// @BasePath /api/v1
func NewGinRouter(training *TrainingHandler, authBaseURL string) *gin.Engine {
	r := gin.New()
	r.Use(gin.Logger(), gin.Recovery())

	// Статические файлы для Swagger
	r.StaticFile("/openapi.yaml", "docs/swagger.yaml")
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// API группа с аутентификацией
	api := r.Group("/api/v1")
	// Создаем middleware с URL auth сервиса
	authMW := NewAuthMiddleware(authBaseURL)
	api.Use(authMW.Handle)
	{
		// ========== Planned Trainings Routes (Запланированные тренировки) ==========
		plannedTrainings := api.Group("/training/planned")
		{
			// GET /training/planned - получить все запланированные тренировки
			plannedTrainings.GET("", training.GetPlannedTrainings)

			// GET /training/planned/{id} - получить запланированную тренировку по ID
			plannedTrainings.GET("/:id", training.GetPlannedTraining)

			// POST /training/planned/create - создать запланированную тренировку
			plannedTrainings.POST("/create", training.CreatePlannedTraining)

			// POST /training/planned/delete/{id} - удалить запланированную тренировку
			plannedTrainings.POST("/delete/:id", training.DeletePlannedTraining)

			// POST /training/planned/update/{id} - обновить запланированную тренировку
			plannedTrainings.POST("/update/:id", training.UpdatePlannedTraining)
		}

		// ========== User Performed Trainings Routes (Выполненные тренировки) ==========
		performedTrainings := api.Group("/training/user_performed")
		{
			// GET /training/user_performed - получить все выполненные тренировки
			performedTrainings.GET("", training.GetUserPerformedTrainings)

			// GET /training/user_performed/{id} - получить выполненную тренировку по ID
			performedTrainings.GET("/:id", training.GetUserPerformedTraining)

			// POST /training/user_performed/create - создать выполненную тренировку
			performedTrainings.POST("/create", training.CreateUserPerformedTraining)

			// POST /training/user_performed/delete/{id} - удалить выполненную тренировку
			performedTrainings.POST("/delete/:id", training.DeleteUserPerformedTraining)

			// POST /training/user_performed/update/{id} - обновить выполненную тренировку
			performedTrainings.POST("/update/:id", training.UpdateUserPerformedTraining)
		}
	}

	return r
}
