package dto

// ErrorResponse представляет ответ об ошибке
type ErrorResponse struct {
	Error string `json:"error" example:"error message" description:"Описание ошибки"`
}
