swag:
	@go run github.com/swaggo/swag/cmd/swag@latest init -g internal/adapter/in/http/router.go --output docs/ --parseDependency --parseInternal

# Install dependencies
deps:
	@echo "Installing dependencies..."
	@go generate ./...
	@go mod download
	@go mod tidy

# Build the application
ARTIFACT_VERSION ?= 0.0.0-local
build: swag deps
	@echo "Building version $(ARTIFACT_VERSION)..."
	@go build \
		-ldflags="-X main.version=$(ARTIFACT_VERSION)" \
		-o ./bin/trainings \
		./cmd/trainings

# Run the application
run: build
	@echo "Running binary..."
	./bin/trainings

# Lint the application
lint:
	@echo "Linting..."
	@go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@golangci-lint run --tests=false --disable-all --timeout=2m -p error

# Build docker image (optional)
build-image:
	@echo "Building docker image version $(ARTIFACT_VERSION)..."
	@docker build \
		--build-arg ARTIFACT_VERSION=$(ARTIFACT_VERSION) \
		-t trainings:$(ARTIFACT_VERSION) .

# Clean the binary
clean:
	@echo "Cleaning..."
	@rm -rf bin/

# Help
help:
	@echo "Available commands:"
	@echo "  deps          - Install dependencies"
	@echo "  build         - Build the application"
	@echo "  build-image   - Build the docker image (optional)"
	@echo "  run           - Run the application"
	@echo "  lint          - Lint the application"
	@echo "  test          - Test the application"
	@echo "  clean         - Clean the binary"

.DEFAULT_GOAL := help
.PHONY: help build build-image run lint test clean deps gen