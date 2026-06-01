# Exercise Service

Сервис каталога упражнений.

## Описание

Сервис предоставляет информацию об упражнениях, включая названия, теги, ссылки на видео и подробные описания.

## Swagger
```json
{
    "swagger": "2.0",
    "info": {
        "description": "Сервис информации о упражнениях",
        "title": "Enduran Exercise API",
        "contact": {},
        "version": "1.0"
    },
    "basePath": "/api/v1",
    "paths": {
        "/exercise": {
            "get": {
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "exercise"
                ],
                "summary": "Get all exercises",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/github_com_EnduranNSU_exercise_internal_domain.ExerciseRead"
                            }
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    }
                }
            }
        },
        "/exercise/{id}": {
            "get": {
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "exercise"
                ],
                "summary": "Get exercise by ID",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Exercise ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_exercise_internal_domain.ExerciseReadVerbose"
                        }
                    },
                    "404": {
                        "description": "Not Found",
                        "schema": {
                            "type": "object",
                            "additionalProperties": true
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
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
        "github_com_EnduranNSU_exercise_internal_domain.ExerciseRead": {
            "type": "object",
            "properties": {
                "hrefs": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "id": {
                    "type": "integer"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "title": {
                    "type": "string"
                }
            }
        },
        "github_com_EnduranNSU_exercise_internal_domain.ExerciseReadVerbose": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string"
                },
                "hrefs": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "id": {
                    "type": "integer"
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "title": {
                    "type": "string"
                }
            }
        }
    }
}
```