# Training Service

Сервис управления тренировками.

## Описание

Сервис позволяет создавать плановые тренировки (расписание) и отмечать выполненные тренировки.

## Swagger

```json
{
    "swagger": "2.0",
    "info": {
        "description": "Сервис информации о тренировках и упражнения",
        "title": "Enduran Training API",
        "contact": {},
        "version": "1.0"
    },
    "basePath": "/api/v1",
    "paths": {
        "/training/planned": {
            "get": {
                "description": "Возвращает все запланированные тренировки текущего пользователя",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "planned-trainings"
                ],
                "summary": "Получить запланированные тренировки",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.PlannedTraining"
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/planned/create": {
            "post": {
                "description": "Создает новую запланированную тренировку для текущего пользователя",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "planned-trainings"
                ],
                "summary": "Создать запланированную тренировку",
                "parameters": [
                    {
                        "description": "Данные тренировки",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/internal_adapter_in_http.CreatePlannedTrainingRequest"
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Created",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.PlannedTraining"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/planned/delete/{id}": {
            "post": {
                "description": "Удаляет запланированную тренировку по ID",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "planned-trainings"
                ],
                "summary": "Удалить запланированную тренировку",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Training ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "204": {
                        "description": "No Content"
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/planned/update/{id}": {
            "post": {
                "description": "Обновляет запланированную тренировку по ID",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "planned-trainings"
                ],
                "summary": "Обновить запланированную тренировку",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Training ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    },
                    {
                        "description": "Данные тренировки",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/internal_adapter_in_http.CreatePlannedTrainingRequest"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.PlannedTraining"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "404": {
                        "description": "Not Found",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/planned/{id}": {
            "get": {
                "description": "Возвращает запланированную тренировку по её ID",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "planned-trainings"
                ],
                "summary": "Получить запланированную тренировку",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Training ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.PlannedTraining"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "404": {
                        "description": "Not Found",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/user_performed": {
            "get": {
                "description": "Возвращает все выполненные тренировки текущего пользователя",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "performed-trainings"
                ],
                "summary": "Получить выполненные тренировки",
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.UserPerformedTraining"
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/user_performed/create": {
            "post": {
                "description": "Создает новую выполненную тренировку для текущего пользователя",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "performed-trainings"
                ],
                "summary": "Создать выполненную тренировку",
                "parameters": [
                    {
                        "description": "Данные тренировки",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/internal_adapter_in_http.CreateUserPerformedTrainingRequest"
                        }
                    }
                ],
                "responses": {
                    "201": {
                        "description": "Created",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.UserPerformedTraining"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/user_performed/delete/{id}": {
            "post": {
                "description": "Удаляет выполненную тренировку по ID",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "performed-trainings"
                ],
                "summary": "Удалить выполненную тренировку",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Training ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "204": {
                        "description": "No Content"
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/user_performed/update/{id}": {
            "post": {
                "description": "Обновляет выполненную тренировку по ID",
                "consumes": [
                    "application/json"
                ],
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "performed-trainings"
                ],
                "summary": "Обновить выполненную тренировку",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Training ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    },
                    {
                        "description": "Данные тренировки",
                        "name": "request",
                        "in": "body",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/internal_adapter_in_http.CreateUserPerformedTrainingRequest"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.UserPerformedTraining"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "404": {
                        "description": "Not Found",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        },
        "/training/user_performed/{id}": {
            "get": {
                "description": "Возвращает выполненную тренировку по её ID",
                "produces": [
                    "application/json"
                ],
                "tags": [
                    "performed-trainings"
                ],
                "summary": "Получить выполненную тренировку",
                "parameters": [
                    {
                        "type": "integer",
                        "description": "Training ID",
                        "name": "id",
                        "in": "path",
                        "required": true
                    }
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.UserPerformedTraining"
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "401": {
                        "description": "Unauthorized",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "404": {
                        "description": "Not Found",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    },
                    "500": {
                        "description": "Internal Server Error",
                        "schema": {
                            "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse"
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "github_com_EnduranNSU_trainings_internal_adapter_in_http_dto.ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "string",
                    "example": "error message"
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.Exercise": {
            "type": "object",
            "properties": {
                "description": {
                    "description": "указатель для nullable поля",
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
        },
        "github_com_EnduranNSU_trainings_internal_domain.PerfomableExercise": {
            "type": "object",
            "properties": {
                "exercise": {
                    "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.Exercise"
                },
                "exercise_id": {
                    "type": "integer"
                },
                "id": {
                    "type": "integer"
                },
                "sets": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.Set"
                    }
                },
                "training_id": {
                    "type": "integer"
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.PerfomableExerciseCreateParams": {
            "type": "object",
            "properties": {
                "exercise_id": {
                    "type": "integer"
                },
                "sets": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.SetCreateParams"
                    }
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.PlannedTraining": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "training": {
                    "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.Training"
                },
                "training_id": {
                    "type": "integer"
                },
                "user_id": {
                    "type": "integer"
                },
                "weekdays": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.Set": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "perfomable_exercise_id": {
                    "type": "integer"
                },
                "repetitions": {
                    "description": "указатель для nullable поля",
                    "type": "integer"
                },
                "rest_duration": {
                    "description": "указатель для nullable поля",
                    "type": "integer"
                },
                "weight": {
                    "description": "указатель для nullable поля",
                    "type": "integer"
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.SetCreateParams": {
            "type": "object",
            "properties": {
                "repetitions": {
                    "type": "integer"
                },
                "rest_duration": {
                    "type": "integer"
                },
                "weight": {
                    "type": "integer"
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.Training": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "perfomable_exercises": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.PerfomableExercise"
                    }
                },
                "title": {
                    "type": "string"
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.TrainingCreateParams": {
            "type": "object",
            "properties": {
                "perfomable_exercises": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.PerfomableExerciseCreateParams"
                    }
                },
                "title": {
                    "type": "string"
                }
            }
        },
        "github_com_EnduranNSU_trainings_internal_domain.UserPerformedTraining": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string"
                },
                "id": {
                    "type": "integer"
                },
                "training": {
                    "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.Training"
                },
                "training_id": {
                    "type": "integer"
                },
                "user_id": {
                    "type": "integer"
                }
            }
        },
        "internal_adapter_in_http.CreatePlannedTrainingRequest": {
            "type": "object",
            "required": [
                "training",
                "weekdays"
            ],
            "properties": {
                "training": {
                    "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.TrainingCreateParams"
                },
                "weekdays": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "internal_adapter_in_http.CreateUserPerformedTrainingRequest": {
            "type": "object",
            "required": [
                "date",
                "training"
            ],
            "properties": {
                "date": {
                    "type": "string"
                },
                "training": {
                    "$ref": "#/definitions/github_com_EnduranNSU_trainings_internal_domain.TrainingCreateParams"
                }
            }
        }
    }
}
```