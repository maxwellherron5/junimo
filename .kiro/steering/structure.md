# Project Structure

## Root Directory Layout
```
junimo/
├── src/                    # Rust backend source code
├── src-tauri/             # Tauri application configuration and backend
├── src-ui/                # Frontend web assets (HTML, CSS, JS)
├── migrations/            # SQLx database migrations
├── data/                  # Static game data (items, bundles)
├── tests/                 # Integration and unit tests
├── docs/                  # Project documentation
├── .env                   # Environment variables (not committed)
├── Cargo.toml            # Rust project configuration
├── tauri.conf.json       # Tauri application configuration
└── README.md             # Project overview and setup instructions
```

## Source Code Organization

### Backend (`src/` and `src-tauri/`)
- `main.rs` - Application entry point
- `lib.rs` - Library root with public API
- `models/` - Database models and structs
- `handlers/` - HTTP request handlers/controllers
- `services/` - Business logic layer
- `database/` - Database connection and utilities
- `config/` - Application configuration

### Frontend (`src-ui/`)
- `index.html` - Main application HTML
- `styles/` - CSS stylesheets
- `scripts/` - JavaScript/TypeScript files
- `assets/` - Images, icons, and other static assets

### Database (`migrations/`)
- Numbered migration files (e.g., `001_initial_schema.sql`)
- Up and down migrations for schema changes

### Data (`data/`)
- `items.json` - Stardew Valley item data
- `bundles.json` - Community center bundle information
- `seeds/` - Database seed files

## Naming Conventions

- **Files**: snake_case for Rust files, kebab-case for web assets
- **Directories**: snake_case for Rust modules, kebab-case for web directories
- **Database**: snake_case for tables and columns
- **API Endpoints**: kebab-case (e.g., `/api/community-bundles`)
- **Rust**: snake_case for functions/variables, PascalCase for types/structs