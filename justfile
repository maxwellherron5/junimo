# Junimo - Stardew Valley Helper
# A Rust web application for tracking Stardew Valley bundles and items

# Default recipe - show available commands
default:
    @just --list

# Development Commands
# ===================

# Run the web server in development mode
dev:
    cd src-tauri && cargo run --bin web-server

# Build the web server for development
build:
    cd src-tauri && cargo build --bin web-server

# Build the web server for production (optimized)
build-release:
    cd src-tauri && cargo build --release --bin web-server

# Run the web server in production mode
run-release:
    cd src-tauri && cargo run --release --bin web-server

# Run the Tauri desktop application (legacy)
tauri-dev:
    cd src-tauri && cargo tauri dev

# Build the Tauri desktop application (legacy)
tauri-build:
    cd src-tauri && cargo tauri build

# Database Commands
# =================

# Initialize the database with sample data
db-init:
    python scripts/seed_database.py

# Add missing items to the database
db-add-items:
    python scripts/add_missing_items.py

# Scrape fresh data from Stardew Valley wiki
db-scrape:
    python scripts/scrape_stardew_data.py

# Quality & Testing
# =================

# Run all Rust tests
test:
    cd src-tauri && cargo test

# Run tests with output
test-verbose:
    cd src-tauri && cargo test -- --nocapture

# Check Rust code formatting
fmt-check:
    cd src-tauri && cargo fmt --check

# Format Rust code
fmt:
    cd src-tauri && cargo fmt

# Run Rust linter (clippy)
lint:
    cd src-tauri && cargo clippy -- -D warnings

# Run all quality checks
check: fmt-check lint test

# Fix common issues
fix:
    cd src-tauri && cargo clippy --fix --allow-dirty --allow-staged
    cd src-tauri && cargo fmt

# Deployment
# ==========

# Build for production deployment
deploy-build: build-release
    @echo "Production build complete!"
    @echo "Binary location: src-tauri/target/release/web-server"

# Run production server (assumes build-release was run)
deploy-run:
    cd src-tauri && ./target/release/web-server

# Development Utilities
# =====================

# Clean all build artifacts
clean:
    cd src-tauri && cargo clean
    rm -rf src-tauri/target

# Update Rust dependencies
update:
    cd src-tauri && cargo update

# Check for outdated dependencies
outdated:
    cd src-tauri && cargo outdated

# Install development dependencies
install-deps:
    @echo "Installing Rust toolchain components..."
    rustup component add rustfmt clippy
    @echo "Installing Python dependencies..."
    pip install -r requirements.txt

# Project Information
# ===================

# Show project structure
tree:
    @echo "Project Structure:"
    @tree -I 'target|node_modules|venv|.git' -a

# Show database info
db-info:
    @echo "Database: SQLite (junimo.db)"
    @sqlite3 src-tauri/junimo.db "SELECT 'Items: ' || COUNT(*) FROM items; SELECT 'Bundles: ' || COUNT(*) FROM bundles; SELECT 'Bundle Items: ' || COUNT(*) FROM bundle_items; SELECT 'Progress Entries: ' || COUNT(*) FROM user_progress;"

# Show application URLs
urls:
    @echo "🍄 Junimo Application URLs:"
    @echo "Web Application: http://localhost:3000"
    @echo "API Base URL: http://localhost:3000/api"
    @echo ""
    @echo "API Endpoints:"
    @echo "  GET  /api/items              - List all items"
    @echo "  GET  /api/items/search?q=... - Search items"
    @echo "  GET  /api/bundles            - List all bundles"
    @echo "  GET  /api/bundles/:id/items  - Get bundle items"
    @echo "  GET  /api/progress           - Get user progress"
    @echo "  POST /api/progress/complete  - Mark item complete"
    @echo "  POST /api/progress/incomplete - Mark item incomplete"

# Development workflow shortcuts
# ==============================

# Quick start for new developers
setup: install-deps db-init
    @echo "✅ Setup complete! Run 'just dev' to start the server."

# Full development cycle
dev-cycle: clean build test lint
    @echo "✅ Development cycle complete!"

# Prepare for commit
pre-commit: fmt lint test
    @echo "✅ Ready for commit!"

# Release preparation
release-prep: clean build-release test
    @echo "✅ Release build ready!"