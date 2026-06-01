package httpin

import (
	"encoding/json"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
)

type AuthMiddleware struct {
	client   *http.Client
	authBase string
}

func NewAuthMiddleware(authBase string) *AuthMiddleware {
	return &AuthMiddleware{
		client: &http.Client{
			Timeout: 5 * time.Second,
		},
		authBase: strings.TrimRight(authBase, "/"),
	}
}

type ValidateResponse struct {
	Valid bool `json:"valid"`
	User  struct {
		ID    int    `json:"id"`
		Email string `json:"email"`
		Name  string `json:"name"`
	} `json:"user"`
}

func (m *AuthMiddleware) Handle(c *gin.Context) {
	authHeader := c.GetHeader("Authorization")

	log.Debug().Msgf("Authorization header: %s", authHeader)

	if authHeader == "" {
		log.Warn().Msg("No authorization header")
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "no_authorization_header"})
		return
	}

	// Проверяем формат Bearer
	if !strings.HasPrefix(strings.ToLower(authHeader), "bearer ") {
		log.Warn().Msg("Invalid authorization header format")
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid_token_format"})
		return
	}

	token := strings.TrimPrefix(authHeader, "Bearer ")
	token = strings.TrimPrefix(token, "bearer ")
	token = strings.TrimSpace(token)

	if token == "" {
		log.Warn().Msg("Empty token")
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "empty_token"})
		return
	}

	// Безопасное логирование токена
	tokenPreview := token
	if len(token) > 20 {
		tokenPreview = token[:20] + "..."
	}
	log.Debug().Msgf("Validating token: %s", tokenPreview)

	validateURL := m.authBase + "/api/v1/validate"
	log.Debug().Msgf("Calling auth service at: %s", validateURL)

	req, err := http.NewRequestWithContext(c.Request.Context(), "GET", validateURL, nil)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create request")
		c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "auth_unavailable"})
		return
	}
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := m.client.Do(req)
	if err != nil {
		log.Error().Err(err).Msgf("Failed to call auth service at %s", validateURL)
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "auth_service_unavailable"})
		return
	}
	defer resp.Body.Close()

	log.Debug().Msgf("Auth service response status: %d", resp.StatusCode)

	if resp.StatusCode != http.StatusOK {
		log.Warn().Msgf("Auth service returned non-200 status: %d", resp.StatusCode)
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid_token"})
		return
	}

	var validateResp ValidateResponse
	if err := json.NewDecoder(resp.Body).Decode(&validateResp); err != nil {
		log.Error().Err(err).Msg("Failed to decode auth response")
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid_auth_response"})
		return
	}

	if !validateResp.Valid {
		log.Warn().Msg("Token invalid")
		c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid_token"})
		return
	}

	c.Set("userID", validateResp.User.ID)
	c.Set("userEmail", validateResp.User.Email)
	c.Set("userName", validateResp.User.Name)

	log.Info().Msgf("User authenticated: ID=%d, Email=%s", validateResp.User.ID, validateResp.User.Email)

	c.Next()
}

func GetUserID(c *gin.Context) (int, bool) {
	userID, exists := c.Get("userID")
	if !exists {
		return 0, false
	}
	id, ok := userID.(int)
	return id, ok
}

func GetUserEmail(c *gin.Context) (string, bool) {
	email, exists := c.Get("userEmail")
	if !exists {
		return "", false
	}
	emailStr, ok := email.(string)
	return emailStr, ok
}