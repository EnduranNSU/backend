# Auth Service

Сервис аутентификации и авторизации пользователей.

## Описание

Сервис отвечает за регистрацию пользователей, аутентификацию, выдачу JWT токенов и валидацию токенов для других сервисов.

## API Endpoints

### 1. Регистрация пользователя

Создает нового пользователя в системе.

```http
POST /api/v1/register
Content-Type: application/json
```
#### Request Body:
```json
{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123"
}
```
#### Response (201 Created):
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
}
```
#### Errors
 - 400 Bad Request - неверный формат запроса
 - 409 Conflict - пользователь уже существует

### 2. Вход в систему

Аутентифицирует пользователя и возвращает JWT токен.

```http
POST /api/v1/login
Content-Type: application/json
```
#### Request Body:
```json
{
    "username": "user@example.com",
    "password": "securepassword123"
}
```
#### Response (200 Ok):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```
#### Errors
 - 400 Bad Request - неверный формат запроса
 - 401 Unauthorized - неверные учетные данные

### 3. Валидация токена

Проверяет валидность JWT токена и возвращает информацию о пользователе.

```http
GET /api/v1/validate
Authorization: Bearer <token>
```
#### Response (200 Ok):
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe"
    }
}
```
#### Errors
 - 401 Unauthorized - неверный или просроченный токен

### 4. Информация о текущем пользователе

Возвращает данные аутентифицированного пользователя.

```http
GET /api/v1/user
Authorization: Bearer <token>
```
#### Response (200 Ok):
```json
{
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe"
}
```




## Swagger
```json
{
    "swagger": "2.0",
    "info": {
        "description": "Сервис авторизации",
        "title": "Enduran Training API",
        "contact": {},
        "version": "1.0"
    },
    "basePath": "/api/v1",
    "paths": {
        "/api/v1/login": {
            "post": {
                "description": "Authenticate user and return access token",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "auth"
                ],
                "summary": "Login user",
                "parameters": [
                    {
                        "description": "Login credentials",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/internal_adapter_in_http.LoginRequest"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/auth_internal_auth.Token"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    }
                }
            }
        },
        "/api/v1/register": {
            "post": {
                "description": "Create a new user account",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "auth"
                ],
                "summary": "Register new user",
                "parameters": [
                    {
                        "description": "User registration data",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/auth_internal_domain.UserCreate"
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Created",
                        "schema": {
                            "$ref": "#/definitions/auth_internal_domain.UserRead"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    },
                    "409": {
                        "description": "Conflict",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    }
                }
            }
        },
        "/api/v1/user": {
            "get": {
                "security": [
                    {
                        "BearerAuth": []
                    }
                ],
                "description": "Get authenticated user information",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "user"
                ],
                "summary": "Get current user",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/auth_internal_domain.UserRead"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    }
                }
            }
        },
        "/api/v1/validate": {
            "get": {
                "security": [
                    {
                        "BearerAuth": []
                    }
                ],
                "description": "Check if access token is valid and return user info",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "auth"
                ],
                "summary": "Validate token",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/internal_adapter_in_http.ValidateResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "auth_internal_auth.Token": {
            "type": "object",
            "properties": {
                "access_token": {
                    "type": "string"
                },
                "token_type": {
                    "type": "string"
                }
            }
        },
        "auth_internal_domain.UserCreate": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                }
            }
        },
        "auth_internal_domain.UserRead": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string"
                },
                "id": {
                    "type": "integer"
                },
                "name": {
                    "type": "string"
                }
            }
        },
        "internal_adapter_in_http.LoginRequest": {
            "type": "object",
            "required": [
                "password",
                "username"
            ],
            "properties": {
                "password": {
                    "type": "string"
                },
                "username": {
                    "type": "string"
                }
            }
        },
        "internal_adapter_in_http.UserInfo": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string"
                },
                "id": {
                    "type": "integer"
                },
                "name": {
                    "type": "string"
                }
            }
        },
        "internal_adapter_in_http.ValidateResponse": {
            "type": "object",
            "properties": {
                "user": {
                    "$ref": "#/definitions/internal_adapter_in_http.UserInfo"
                },
                "valid": {
                    "type": "boolean"
                }
            }
        }
    },
    "securityDefinitions": {
        "BearerAuth": {
            "description": "Type \"Bearer\" followed by a space and the access token.",
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    }
}
```