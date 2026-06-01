# Measurements Service

Сервис трекинга измерений пользователя.

## Описание

Сервис позволяет отслеживать различные измерения пользователя: вес, рост, процент жира, окружности и другие параметры.

## Swagger
```json
{
    "swagger": "2.0",
    "info": {
        "description": "Сервис информации о пользователе (вес, рост, возраст и т.д.)",
        "title": "Enduran User Info API",
        "contact": {},
        "version": "1.0"
    },
    "basePath": "/api/v1",
    "paths": {
        "/measurements": {
            "get": {
                "security": [
                    {
                        "BearerAuth": []
                    }
                ],
                "description": "Возвращает все измерения пользователя",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "measurements"
                ],
                "summary": "Получить все измерения",
                "parameters": [
                    {
                        "type": "string",
                        "description": "Bearer access токен",
                        "name": "Authorization",
                        "in": "header",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementResponse"
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/measurements/create": {
            "post": {
                "security": [
                    {
                        "BearerAuth": []
                    }
                ],
                "description": "Создает новое измерение для пользователя",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "measurements"
                ],
                "summary": "Создать измерение",
                "parameters": [
                    {
                        "type": "string",
                        "description": "Bearer access токен",
                        "name": "Authorization",
                        "in": "header",
                        "required": true
                    },
                    {
                        "description": "Данные измерения",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementBaseRequest"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementResponse"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/measurements/update": {
            "post": {
                "security": [
                    {
                        "BearerAuth": []
                    }
                ],
                "description": "Удаляет все старые измерения и создает новые",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "measurements"
                ],
                "summary": "Обновить все измерения",
                "parameters": [
                    {
                        "type": "string",
                        "description": "Bearer access токен",
                        "name": "Authorization",
                        "in": "header",
                        "required": true
                    },
                    {
                        "description": "Массив измерений",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementBaseRequest"
                            }
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementResponse"
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "error message"
                }
            }
        },
        "github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementBaseRequest": {
            "type": "object",
            "required": [
                "date",
                "type",
                "value"
            ],
            "properties": {
                "date": {
                    "type": "string"
                },
                "type": {
                    "type": "string"
                },
                "value": {
                    "type": "integer",
                    "minimum": 0
                }
            }
        },
        "github_com_EnduranNSU_end-user-info_internal_adapter_in_http_dto.MeasurementResponse": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string"
                },
                "id": {
                    "type": "integer"
                },
                "type": {
                    "type": "string"
                },
                "value": {
                    "type": "integer"
                }
            }
        }
    }
}
```