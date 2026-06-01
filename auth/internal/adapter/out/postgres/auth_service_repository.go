package postgres

import (
	"context"
	"database/sql"
	"errors"
	"fmt"

	"auth/internal/adapter/out/postgres/gen"
	"auth/internal/domain"
)

type UserRepositoryImpl struct {
	db      *sql.DB
	queries *gen.Queries
}

func NewUserRepository(db *sql.DB) domain.UserRepository {
	return &UserRepositoryImpl{
		db:      db,
		queries: gen.New(db),
	}
}

// CreateUser создает нового пользователя
func (r *UserRepositoryImpl) CreateUser(ctx context.Context, userIn domain.UserCreate, hashedPassword string) (*domain.UserRead, error) {
	// Создаем пользователя в БД
	dbUser, err := r.queries.CreateUser(ctx, gen.CreateUserParams{
		Email:          userIn.Email,
		Name:           userIn.Name,
		HashedPassword: hashedPassword,
	})
	if err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	// Возвращаем UserRead (как в Python версии)
	return &domain.UserRead{
		ID:    int(dbUser.ID),
		Email: dbUser.Email,
		Name:  dbUser.Name,
	}, nil
}

// GetUserAuth возвращает пользователя с хешированным паролем
func (r *UserRepositoryImpl) GetUserAuth(ctx context.Context, email string) (*domain.UserAuth, error) {
	dbUser, err := r.queries.GetUserByEmail(ctx, email)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			// Как в Python: возвращаем None -> nil
			return nil, nil
		}
		return nil, fmt.Errorf("failed to get user by email: %w", err)
	}

	// Возвращаем UserAuth с хешированным паролем
	return &domain.UserAuth{
		ID:             int(dbUser.ID),
		Email:          dbUser.Email,
		Name:           dbUser.Name,
		HashedPassword: dbUser.HashedPassword,
	}, nil
}

// GetUser возвращает пользователя без хешированного пароля
func (r *UserRepositoryImpl) GetUser(ctx context.Context, email string) (*domain.UserRead, error) {
	dbUser, err := r.queries.GetUserByEmail(ctx, email)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			// Как в Python: возвращаем None -> nil
			return nil, nil
		}
		return nil, fmt.Errorf("failed to get user by email: %w", err)
	}

	// Возвращаем UserRead (как в Python версии)
	return &domain.UserRead{
		ID:    int(dbUser.ID),
		Email: dbUser.Email,
		Name:  dbUser.Name,
	}, nil
}

// GetUserByID возвращает пользователя по ID
func (r *UserRepositoryImpl) GetUserByID(ctx context.Context, userID int) (*domain.UserRead, error) {
	dbUser, err := r.queries.GetUserByID(ctx, int32(userID))
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			// Как в Python: возвращаем None -> nil
			return nil, nil
		}
		return nil, fmt.Errorf("failed to get user by id: %w", err)
	}

	// Возвращаем UserRead (как в Python версии)
	return &domain.UserRead{
		ID:    int(dbUser.ID),
		Email: dbUser.Email,
		Name:  dbUser.Name,
	}, nil
}
