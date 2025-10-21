# Junimo

Tired of using a spreadsheet and a million tabs open on the stardew wiki to track your progress? Same! Junimo is your friendly stardew companion used to help you track your progress.


## Features

- **Item Browser** - Search and browse all 161+ Stardew Valley items
- **Bundle Tracker** - View all 23 Community Center bundles with required items
- **Progress Tracking** - Check off items as you collect them
- **Progress Statistics** - Visual progress bars and completion percentages
- **Persistent Storage** - Progress saved to SQLite database

##  Quick Start

### Prerequisites

- [Rust](https://rustup.rs/) (latest stable)
- [Just](https://github.com/casey/just) command runner
- Python 3.7+ (for data scraping, optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd junimo
   ```

2. **Setup the project**
   ```bash
   just setup
   ```

3. **Start the development server**
   ```bash
   just dev
   ```

4. **Open your browser**
   Visit [http://localhost:3000](http://localhost:3000)

## Development

### Available Commands

```bash
# Development
just dev              # Start development server
just build            # Build for development
just build-release    # Build for production

# Database
just db-init          # Initialize database with sample data
just db-scrape        # Scrape fresh data from wiki

# Quality & Testing
just test             # Run tests
just lint             # Run linter
just fmt              # Format code
just check            # Run all quality checks

# Utilities
just clean            # Clean build artifacts
just urls             # Show application URLs
just db-info          # Show database statistics
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Stardew Valley](https://www.stardewvalley.net/) by ConcernedApe (my hero)
- [Stardew Valley Wiki](https://stardewvalleywiki.com/) for item and bundle data

I hope this helps your stardew needs :D