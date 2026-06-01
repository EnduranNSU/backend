package main

import (
	"github.com/EnduranNSU/trainings/internal/adapter/out/postgres"
	"github.com/EnduranNSU/trainings/internal/app"
	"github.com/EnduranNSU/trainings/internal/logging"
	gorm "github.com/EnduranNSU/trainings/internal/util/db"
	_ "github.com/joho/godotenv/autoload"
	_ "github.com/lib/pq"
	"github.com/num30/config"
	"github.com/rs/zerolog/log"
)

func init() {
	// Setup default logger
	logging.SetupLogger(
		logging.Config{
			Level: "info",
			Console: logging.ConsoleLoggerConfig{
				Enable:   true,
				Encoding: "text",
			},
			File: logging.FileLoggerConfig{
				Enable: false,
			},
		},
	)
}

// @title           Enduran Training API
// @version         1.0
// @description     Сервис информации о тренировках и упражнения
// @BasePath        /api/v1
// @schemes         http
// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
func main() {
	// Load config
	var cfg app.Config
	configName := app.GetConfigName()

	err := config.NewConfReader(configName).WithPrefix("APP").Read(&cfg)
	if err != nil {
		log.Fatal().Stack().Err(err).
			Str("service", "trainings").Msg("failed to load config")
	}

	// Setup logger
	logging.SetupLogger(toLoggerConfig(cfg.Logger))

	db, err := gorm.NewDBConnection(cfg.Db.Host, cfg.Db.User, cfg.Db.Password, cfg.Db.Dbname, cfg.Db.Port)
	if err != nil {
		log.Fatal().Stack().Err(err).
			Str("service", "trainings").Msgf("Failed to connect to database: %v", err)
	}

	// Init repo - теперь без возврата ошибки
	trepo := postgres.NewTrainingRepositoryGorm(db)

	srv := app.SetupServer(trepo, cfg.Http.Addr, cfg.Auth.BaseURL)

	if err := srv.StartServer(); err != nil {
		log.Fatal().Err(err).
			Str("service", "trainings").Msg("http server stopped")
	}
}

func toLoggerConfig(cfg app.LoggerConfig) logging.Config {
	return logging.Config{
		Level: cfg.Level,
		Console: logging.ConsoleLoggerConfig{
			Enable:   cfg.Console.Enable,
			Encoding: cfg.Console.Encoding,
		},
		File: logging.FileLoggerConfig{
			Enable:  cfg.File.Enable,
			DirPath: cfg.File.DirPath,
			MaxSize: cfg.File.MaxSize,
			MaxAge:  cfg.File.MaxAge,
		},
	}
}
