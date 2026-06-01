package main

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/EnduranNSU/end-user-info/internal/adapter/out/postgres"
	"github.com/EnduranNSU/end-user-info/internal/app"
	"github.com/EnduranNSU/end-user-info/internal/logging"
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

// @title           Enduran User Info API
// @version         1.0
// @description     Сервис информации о пользователе (вес, рост, возраст и т.д.)
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
		log.Fatal().Stack().Err(err).Msg("failed to load config")
	}

	// Setup logger
	logging.SetupLogger(toLoggerConfig(cfg.Logger))

	// Open db
	db, err := sql.Open("postgres",
		fmt.Sprintf(
			"user=%s password=%s dbname=%s sslmode=disable host=%s port=%d",
			cfg.Db.User, cfg.Db.Password, cfg.Db.Dbname, cfg.Db.Host, cfg.Db.Port))
	if err != nil {
		log.Fatal().Stack().Err(err).Msgf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Checking connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := db.PingContext(ctx); err != nil {
		log.Fatal().Stack().Err(err).Msgf("Failed to ping database: %v", err)
	}

	// Init repo - теперь без возврата ошибки
	repo := postgres.NewMeasurementRepository(db)

	srv := app.SetupServer(repo, cfg.Http.Addr, cfg.Auth.BaseURL)

	if err := srv.StartServer(); err != nil {
		log.Fatal().Err(err).Msg("http server stopped")
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
