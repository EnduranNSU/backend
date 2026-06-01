package app

import (
	"strings"

	"auth/internal/utils/env"

	"github.com/spf13/viper"
)

func GetConfigName() string {
	configPath := env.GetEnvWithDefault("APP_CONFIG_FILE", "config/config.yaml")
	oldnew := make([]string, 2*len(viper.SupportedExts))
	for i, ext := range viper.SupportedExts {
		oldnew[2*i] = "." + ext
		oldnew[2*i+1] = ""
	}
	return strings.NewReplacer(oldnew...).Replace(configPath)
}

type Config struct {
	HTTP           HTTPConfig     `mapstructure:"http"`
	DB             DBConfig       `mapstructure:"db"`
	Logger         LoggerConfig   `mapstructure:"logger"`
	Authentication Authentication `mapstructure:"auth"`
}

type HTTPConfig struct {
	Addr string `mapstructure:"addr" default:":8081"`
}

type Authentication struct {
	SecretKey                    string `mapstructure:"secret_key"`
	Algorithm                    string `mapstructure:"algorithm"`
	AccessTokenExpirationMinutes int    `mapstructure:"access_token_expiration_minutes"`
}

type DBConfig struct {
	DSN string `mapstructure:"dsn" default:"postgres://postgres:postgres@localhost:5432/auth?sslmode=disable"`
}

type LogEncoding string

const (
	LogLevelDebug = LogLevel("debug")
	LogLevelInfo  = LogLevel("info")
	LogLevelWarn  = LogLevel("warning")
	LogLevelError = LogLevel("error")
)

type LogLevel string

const (
	LogEncodingText = LogEncoding("text")
	LogEncodingJSON = LogEncoding("json")
)

type LoggerConfig struct {
	Level   string `default:"info" validate:"oneof=debug info warning error"`
	Console ConsoleLoggerConfig
	File    FileLoggerConfig
}

type ConsoleLoggerConfig struct {
	Enable   bool   `default:"true"`
	Encoding string `default:"text" validate:"required_with=Enable,oneof=text json"`
}

type FileLoggerConfig struct {
	Enable  bool   `default:"false"`
	DirPath string `default:"logs" validate:"required_with=Enable"`
	MaxSize int    `default:"100" validate:"required_with=Enable,min=0"`
	MaxAge  int    `default:"30" validate:"required_with=Enable,min=0"`
}
