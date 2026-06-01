package main

import (
	"github.com/EnduranNSU/exercise/internal/adapter/out/postgres"
	"github.com/EnduranNSU/exercise/internal/app"
	"github.com/EnduranNSU/exercise/internal/logging"
	"github.com/EnduranNSU/exercise/internal/minio"
	gorm "github.com/EnduranNSU/exercise/internal/util/db"
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
			Str("service", "exercise").Msg("failed to load config")
	}

	// Setup logger
	logging.SetupLogger(toLoggerConfig(cfg.Logger))

	db, err := gorm.NewDBConnection(cfg.Db.Host, cfg.Db.User, cfg.Db.Password, cfg.Db.Dbname, cfg.Db.Port)
	if err != nil {
		log.Fatal().Stack().Err(err).
			Str("service", "exercise").Msgf("Failed to connect to database: %v", err)
	}

	s3Client, err := minio.NewS3Client(
		cfg.S3.Host, cfg.S3.User, cfg.S3.Password, cfg.S3.Secure, cfg.S3.Bucket,
	)
	if err != nil {
		log.Fatal().Err(err).
			Str("service", "exercise").Msgf("minio error: %s", cfg.S3.Host)
	}

	// Создание репозитория
	repo := postgres.NewExerciseRepositoryGorm(db, s3Client)

	srv := app.SetupServer(repo, cfg.Http.Addr, cfg.Auth.BaseURL)

	if err := srv.StartServer(); err != nil {
		log.Fatal().Err(err).
			Str("service", "exercise").Msg("http server stopped")
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
