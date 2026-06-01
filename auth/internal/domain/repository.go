package domain

import "context"

type UserRepository interface {
	// CreateUser создает нового пользователя и возвращает созданную запись
	CreateUser(ctx context.Context, userIn UserCreate, hashedPassword string) (*UserRead, error)

	// GetUserAuth возвращает пользователя с хешированным паролем для аутентификации
	GetUserAuth(ctx context.Context, email string) (*UserAuth, error)

	// GetUser возвращает пользователя без хешированного пароля
	GetUser(ctx context.Context, email string) (*UserRead, error)

	// GetUserByID возвращает пользователя по ID
	GetUserByID(ctx context.Context, userID int) (*UserRead, error)
}
