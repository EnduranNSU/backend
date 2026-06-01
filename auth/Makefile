# ===== Generate Swagger =====
swag:
	@echo "Generating swagger documentation..."
	@go run github.com/swaggo/swag/cmd/swag@latest init \
		-g cmd/auth/main.go \
		--output docs/ \
		--parseDependency \
		--parseInternal
	@echo "Swagger documentation generated in docs/"

# ===== Generate sqlc =====
sqlc:
	@echo "Generating sqlc code..."
	@go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest
	@cd config && sqlc generate
	@echo "sqlc code generated"

# ===== Generate all code =====
gen: sqlc swag
	@echo "All code generated successfully"
	@ls -la docs/  # Проверяем что файлы создались

# ===== Dependencies =====
deps:
	@echo "Installing dependencies..."
	@go mod download
	@go mod tidy

# ===== Build =====
ARTIFACT_VERSION ?= 0.0.0-local

build: gen deps
	@echo "Building version $(ARTIFACT_VERSION)..."
	@mkdir -p bin
	@go build \
		-o ./bin/auth \
		./cmd/auth

# ===== Run locally =====
run: build
	@echo "Running binary..."
	./bin/auth

# ===== Lint =====
lint:
	@echo "Linting..."
	@go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@golangci-lint run --tests=false --disable-all --timeout=2m -p error

# ===== Tests =====
test:
	@echo "Testing..."
	@go test -v -race ./internal/...

coverage:
	@echo "Coverage..."
	@go test -race -coverprofile=coverage.out -covermode=atomic ./internal/...
	@go tool cover -html=coverage.out -o coverage.html

# ===== Docker image =====
build-image:
	@echo "Building docker image version $(ARTIFACT_VERSION)..."
	@docker build \
		--build-arg ARTIFACT_VERSION=$(ARTIFACT_VERSION) \
		-t enduran-auth:$(ARTIFACT_VERSION) .

# ===== Cleanup =====
clean:
	@echo "Cleaning..."
	@rm -rf bin/
	@rm -rf docs/
	@rm -f coverage.out coverage.html

# ===== Help =====
help:
	@echo "Available commands:"
	@echo "  make gen          - Generate sqlc + swagger"
	@echo "  make build        - Build the application"
	@echo "  make run          - Run the application locally"
	@echo "  make build-image  - Build Docker image"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"

.PHONY: gen sqlc swag deps build run clean test coverage lint build-image help