package app

import (
	"context"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	httpin "github.com/EnduranNSU/end-user-info/internal/adapter/in/http"
	"github.com/EnduranNSU/end-user-info/internal/domain"
	"github.com/rs/zerolog/log"
)

type Server struct {
	Svc         domain.MeasurementRepository
	Addr        string
	AuthBaseURL string
}

func SetupServer(svc domain.MeasurementRepository, addr, authBaseURL string) *Server {
	return &Server{
		Svc:         svc,
		Addr:        addr,
		AuthBaseURL: authBaseURL,
	}
}

func (s *Server) StartServer() error {
	h := httpin.NewMeasurementHandler(s.Svc)
	engine := httpin.NewGinRouter(h, s.AuthBaseURL)

	srv := &http.Server{
		Addr:              s.Addr,
		Handler:           engine,
		ReadHeaderTimeout: 5 * time.Second,
	}
	// Запуск сервера в отдельной горутине
	go func() {
		log.Info().Msgf("HTTP server starting on %s", s.Addr)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatal().Err(err).Msg("HTTP server error")
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info().Msg("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Error().Err(err).Msg("HTTP server forced to shutdown")
		return err
	}

	log.Info().Msg("Server stopped gracefully")
	return nil
}
