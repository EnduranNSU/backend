package auth

type Token struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
}

func NewToken(accessToken string) *Token {
	return &Token{
		AccessToken: accessToken,
		TokenType:   "bearer",
	}
}
