package auth

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/rs/zerolog/log"
)

type JWTConfig struct {
	SecretKey                    string
	Algorithm                    string
	AccessTokenExpirationMinutes int
}

type JWTService struct {
	config JWTConfig
}

func NewJWTService(secretKey string, algorithm string, access int) *JWTService {
	return &JWTService{
		config: JWTConfig{
			SecretKey:                    secretKey,
			Algorithm:                    algorithm,
			AccessTokenExpirationMinutes: access,
		},
	}
}

func (s *JWTService) CreateAccessToken(email string) (string, error) {
	expirationTime := time.Now().Add(time.Duration(s.config.AccessTokenExpirationMinutes) * time.Minute)

	claims := jwt.MapClaims{
		"sub": email,
		"exp": expirationTime.Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(s.config.SecretKey))
	if err != nil {
		log.Error().Err(err).Msg("Failed to sign token")
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	log.Debug().Msgf("Created token for %s (expires: %v): %s",
		email, expirationTime, tokenString[:50]+"...")

	return tokenString, nil
}

func (s *JWTService) ValidateToken(tokenString string) (string, error) {
    // Безопасное логирование токена
    tokenPreview := tokenString
    if len(tokenString) > 20 {
        tokenPreview = tokenString[:20] + "..."
    }
    log.Debug().Msgf("Validating token: %s", tokenPreview)
    
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return []byte(s.config.SecretKey), nil
    })

    if err != nil {
        log.Error().Err(err).Msg("Failed to parse token")
        return "", fmt.Errorf("failed to parse token: %w", err)
    }

    if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
        email, ok := claims["sub"].(string)
        if !ok {
            return "", fmt.Errorf("invalid token claims")
        }
        
        if exp, ok := claims["exp"]; ok {
            expTime := time.Unix(int64(exp.(float64)), 0)
            log.Debug().Msgf("Token expires at: %v, current time: %v", expTime, time.Now())
            if expTime.Before(time.Now()) {
                log.Error().Msgf("Token expired at: %v", expTime)
                return "", fmt.Errorf("token expired")
            }
        }
        
        return email, nil
    }

    return "", fmt.Errorf("invalid token")
}

func maskSecret(secret string) string {
	if len(secret) > 10 {
		return secret[:5] + "..." + secret[len(secret)-5:]
	}
	return "***"
}
