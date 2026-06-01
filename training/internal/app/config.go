package app

import (
	"strings"

	"github.com/spf13/viper"

	"github.com/EnduranNSU/trainings/internal/util/env"
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
	Db     DbConfig
	Logger LoggerConfig
	Http   HttpConfig
	Auth   AuthConfig
}

type AuthConfig struct {
	BaseURL string `mapstructure:"base_url" default:"http://localhost:8081"`
}

type HttpConfig struct {
	Addr string `default:":8080"`
}

type DbConfig struct {
	User     string
	Password string
	Dbname   string
	Host     string
	Port     int32
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
