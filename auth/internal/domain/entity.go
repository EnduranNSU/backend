package domain

type UserBase struct {
	Email string `json:"email"`
	Name  string `json:"name"`
}

type UserCreate struct {
	UserBase
	Password string `json:"password"`
}

type UserRead struct {
	ID    int    `json:"id"`
	Email string `json:"email"`
	Name  string `json:"name"`
}

type UserAuth struct {
	ID             int    `json:"id"`
	Email          string `json:"email"`
	Name           string `json:"name"`
	HashedPassword string `json:"-"` // Не возвращаем в JSON
}
