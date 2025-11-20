# Olympus Transcriber - Development Makefile

.PHONY: help install test lint format clean run setup-daemon stop-daemon logs

help:
	@echo "Olympus Transcriber - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        - Install dependencies"
	@echo "  make setup-daemon   - Install as LaunchAgent"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run locally"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo ""
	@echo "Daemon Control:"
	@echo "  make stop-daemon   - Stop LaunchAgent"
	@echo "  make logs          - Watch logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove build artifacts"

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "Done!"

test:
	@echo "Running tests..."
	pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

lint:
	@echo "Running linters..."
	flake8 src/
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/
	@echo "Code formatted!"

run:
	@echo "Starting Olympus Transcriber..."
	python src/main.py

setup-daemon:
	@echo "Installing LaunchAgent..."
	chmod +x setup.sh
	./setup.sh

stop-daemon:
	@echo "Stopping LaunchAgent..."
	launchctl unload ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
	@echo "Stopped!"

reload-daemon:
	@echo "Reloading LaunchAgent..."
	launchctl unload ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
	launchctl load ~/Library/LaunchAgents/com.user.olympus-transcriber.plist
	@echo "Reloaded!"

logs:
	@echo "Watching logs (Ctrl+C to stop)..."
	tail -f ~/Library/Logs/olympus_transcriber.log

daemon-logs:
	@echo "Watching LaunchAgent logs (Ctrl+C to stop)..."
	tail -f /tmp/olympus-transcriber-out.log

status:
	@echo "Daemon status:"
	@launchctl list | grep olympus-transcriber || echo "Not running"

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "Cleaned!"

dev-setup:
	@echo "Setting up development environment..."
	python3 -m venv venv
	@echo "Virtual environment created!"
	@echo "Now run: source venv/bin/activate && make install"


