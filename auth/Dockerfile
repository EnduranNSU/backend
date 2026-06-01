# Многоуровневая сборка для Go приложения
ARG GOLANG_VERSION=1.25-alpine3.21
ARG ALPINE_VERSION=3.21

# Этап 1: Загрузка зависимостей
FROM golang:${GOLANG_VERSION} AS deps

WORKDIR /app

# Копируем файлы зависимостей в первую очередь для кэширования
COPY go.mod go.sum ./
RUN go mod download

# Устанавливаем sqlc и swag на этом этапе
RUN go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.30.0
RUN go install github.com/swaggo/swag/cmd/swag@latest

# Этап 2: Сборка приложения
FROM deps AS builder

# Копируем исходный код
COPY . .

# Устанавливаем необходимые инструменты для сборки
RUN apk add --no-cache make git

# Добавляем бинарники в PATH
ENV PATH="/go/bin:${PATH}"

# Генерируем код и документацию ДО сборки
RUN make gen

# Проверяем, что docs были созданы и показываем их содержимое
RUN ls -la /app/docs/ || echo "No docs directory found"

# Сборка приложения
ENV CGO_ENABLED=0
ARG ARTIFACT_VERSION
ARG GOOS=linux
ARG GOARCH=amd64

RUN make build

# Этап 3: Runtime - минимальный образ
FROM alpine:${ALPINE_VERSION} AS runtime

# Устанавливаем метаданные
LABEL maintainer="your-team@example.com"
LABEL description="Auth service"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем бинарник из этапа сборки
COPY --from=builder /app/bin/auth /app/auth

# Копируем документацию, ЕСЛИ она существует
COPY --from=builder /app/docs /app/docs/

# Устанавливаем необходимые системные пакеты
RUN apk update \
    && apk add --no-cache --upgrade \
        bash \
        ca-certificates \
        curl \
        tzdata \
        libc6-compat \
    && update-ca-certificates \
    && rm -rf /var/cache/apk/*

# Настраиваем часовой пояс
RUN echo 'Etc/UTC' > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime

# Создаем непривилегированного пользователя
RUN addgroup -g 1001 -S appgroup \
    && adduser -u 1001 -S appuser -G appgroup -h /app \
    && chown -R appuser:appgroup /app

# Проверяем наличие файлов документации
RUN ls -la /app/docs/ || echo "No docs directory in runtime"

# Настройки окружения
ENV TZ=Etc/UTC
ENV LANG=en_US.utf8
ENV LC_ALL=en_US.UTF-8

# Переключаемся на непривилегированного пользователя
USER appuser

# Запуск приложения
ENTRYPOINT ["/app/auth"]