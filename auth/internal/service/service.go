package service

import (
	"context"
	"fmt"

	"auth/internal/auth"
	"auth/internal/domain"
)

type AuthService struct {
	userService domain.UserRepository
	jwtService  *auth.JWTService
}

func NewAuthService(userService domain.UserRepository, jwtService *auth.JWTService) *AuthService {
	return &AuthService{
		userService: userService,
		jwtService:  jwtService,
	}
}

func (s *AuthService) AuthenticateUser(ctx context.Context, email, password string) (*domain.UserAuth, error) {
	user, err := s.userService.GetUserAuth(ctx, email)
	if err != nil {
		return nil, fmt.Errorf("failed to get user: %w", err)
	}

	if user == nil {
		return nil, nil
	}

	if !auth.Verify(password, user.HashedPassword) {
		return nil, nil
	}

	return user, nil
}

func (s *AuthService) CreateAccessToken(email string) (string, error) {
	return s.jwtService.CreateAccessToken(email)
}
