package main

import (
	"auth/internal/app"
	"auth/internal/logging"

	_ "github.com/joho/godotenv/autoload"
	"github.com/num30/config"
	"github.com/rs/zerolog/log"
)

func init() {
	logging.SetupLogger(logging.Config{
		Level: "info",
		Console: logging.ConsoleLoggerConfig{
			Enable:   true,
			Encoding: "text",
		},
		File: logging.FileLoggerConfig{
			Enable: false,
		},
	})
}

// @title Enduran Training API
// @version 1.0
// @description Сервис авторизации
// @BasePath /api/v1
// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description Type "Bearer" followed by a space and the access token.
func main() {
	var cfg app.Config
	cfgName := app.GetConfigName()
	if err := config.NewConfReader(cfgName).WithPrefix("APP").Read(&cfg); err != nil {
		log.Fatal().Stack().Err(err).Msg("failed to load config")
	}

	logging.SetupLogger(toLoggerConfig(cfg.Logger))

	srv, err := app.BuildServer(cfg)
	if err != nil {
		log.Fatal().Stack().Err(err).Msg("failed to build server")
	}

	if err := srv.Start(); err != nil {
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
