package domain

import "errors"

var (
	ErrNotFound       = errors.New("not found")
	ErrAlreadyExists  = errors.New("already exists")
	ErrInvalidCreds   = errors.New("invalid credentials")
	ErrBlockedUser    = errors.New("user is blocked")
	ErrInvalidRefresh = errors.New("invalid refresh token")
	ErrInvalidOTP     = errors.New("invalid or expired otp")
)
