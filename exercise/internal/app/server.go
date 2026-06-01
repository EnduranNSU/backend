package app

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	httpin "github.com/EnduranNSU/exercise/internal/adapter/in/http"
	"github.com/EnduranNSU/exercise/internal/domain"
	"github.com/rs/zerolog/log"
)

type Server struct {
	TrainingSvc domain.ExerciseRepository
	Addr        string
	AuthBaseURL string
}

func SetupServer(trainingSvc domain.ExerciseRepository, addr string, authBaseURL string) *Server {
	return &Server{
		TrainingSvc: trainingSvc,
		Addr:        addr,
		AuthBaseURL: authBaseURL,
	}
}

func (s *Server) StartServer() error {
	th := httpin.NewTrainingHandler(s.TrainingSvc)
	engine := httpin.NewGinRouter(th, s.AuthBaseURL)

	srv := &http.Server{
		Addr:              s.Addr,
		Handler:           engine,
		ReadHeaderTimeout: 5 * time.Second,
	}
	// Запуск сервера в отдельной горутине
	go func() {
		log.Info().Msgf("HTTP server starting on %s", s.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).
				Str("service", "trainings").Msg("HTTP server error")
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info().
		Str("service", "trainings").Msg("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Error().Err(err).
			Str("service", "trainings").Msg("HTTP server forced to shutdown")
		return err
	}

	log.Info().
		Str("service", "trainings").Msg("Server stopped gracefully")
	return nil
}
