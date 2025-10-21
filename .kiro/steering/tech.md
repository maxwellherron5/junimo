# Technology Stack

## Backend
- **Language**: Rust
- **Database**: SQLx with PostgreSQL/SQLite
- **Web Framework**: Likely Axum or Actix-web for API endpoints

## Frontend
- **Framework**: Tauri (Rust-based desktop app framework)
- **Web Technologies**: HTML, CSS, JavaScript/TypeScript within Tauri webview
- **UI**: Native desktop application with web-based UI

## Database
- **ORM**: SQLx for compile-time checked SQL queries
- **Migrations**: SQLx migrations for database schema management
- **Database**: PostgreSQL for production, SQLite for development/testing

## Common Commands

### Development
```bash
# Run the application in development mode
cargo tauri dev

# Build the backend only
cargo build

# Run database migrations
sqlx migrate run

# Create new migration
sqlx migrate add <migration_name>
```

### Testing
```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test <test_name>
```

### Database
```bash
# Setup database URL (add to .env)
DATABASE_URL=sqlite:junimo.db

# Prepare SQLx for offline compilation
cargo sqlx prepare
```

### Build & Release
```bash
# Build for production
cargo tauri build

# Build backend only (release)
cargo build --release
```