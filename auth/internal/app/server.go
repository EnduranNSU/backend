package app

import (
	"context"
	"database/sql"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	httpin "auth/internal/adapter/in/http"
	"auth/internal/adapter/out/postgres"
	"auth/internal/auth"
	"auth/internal/service"

	_ "github.com/lib/pq"
	"github.com/rs/zerolog/log"
)

type Server struct {
	httpSrv *http.Server
	db      *sql.DB
}

func BuildServer(cfg Config) (*Server, error) {

	db, err := sql.Open("postgres", cfg.DB.DSN)
	if err != nil {
		return nil, err
	}
	{
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := db.PingContext(ctx); err != nil {
			_ = db.Close()
			return nil, err
		}
	}

	repos := postgres.NewUserRepository(db)
	jwtService := auth.NewJWTService(
		cfg.Authentication.SecretKey, cfg.Authentication.Algorithm, cfg.Authentication.AccessTokenExpirationMinutes,
	)
	svc := service.NewAuthService(repos, jwtService)

	authController := httpin.NewAuthController(svc)
	middleware := httpin.NewAuthMiddleware(jwtService, repos)
	signupController := httpin.NewSignupController(repos)
	userController := httpin.NewUserController()
	engine := httpin.NewGinRouter(&httpin.RouterConfig{
		AuthController:   authController,
		AuthMiddleware:   middleware,
		SignupController: signupController,
		UserController:   userController,
	})

	srv := &http.Server{
		Addr:              cfg.HTTP.Addr,
		Handler:           engine,
		ReadHeaderTimeout: 5 * time.Second,
	}

	return &Server{httpSrv: srv, db: db}, nil
}

func (s *Server) Start() error {
	go func() {
		log.Info().Str("addr", s.httpSrv.Addr).Msg("HTTP server starting")
		if err := s.httpSrv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).Msg("HTTP server error")
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info().Msg("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := s.httpSrv.Shutdown(ctx); err != nil {
		log.Error().Err(err).Msg("HTTP server forced to shutdown")
	}
	_ = s.db.Close()

	log.Info().Msg("Server stopped gracefully")
	return nil
}
