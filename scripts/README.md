# Junimo Data Scripts

This directory contains Python scripts for scraping Stardew Valley data and populating the database.

## Quick Usage

Use the justfile commands instead of running scripts directly:

```bash
just db-init      # Initialize database with data
just db-scrape    # Scrape fresh data from wiki
```

## Scripts Overview

### 1. `scrape_bundles_specific.py`
Creates comprehensive Stardew Valley items and bundles data with accurate information from the game.

**Features:**
- 43+ items with proper IDs, names, descriptions, categories, and stats
- 23 Community Center bundles across all rooms
- Accurate item-to-bundle relationships
- Proper quality specifications for bundle items

**Usage:**
```bash
python scripts/scrape_bundles_specific.py
```

### 2. `scrape_stardew_data.py`
Advanced web scraper that can fetch data directly from the Stardew Valley wiki (experimental).

**Features:**
- Scrapes multiple item categories from wiki pages
- Extracts detailed item information
- Parses bundle requirements from wiki tables
- Handles rate limiting and error recovery

**Usage:**
```bash
python scripts/scrape_stardew_data.py
```

### 3. `seed_database.py`
Database seeding utility that populates the SQLite database with items and bundles data.

**Features:**
- Loads data from JSON files
- Clears existing data safely
- Seeds items, bundles, and bundle_items tables
- Provides data verification and statistics

**Usage:**
```bash
python scripts/seed_database.py --db junimo.db
python scripts/seed_database.py --generate-data  # Generate data first
```

### 4. `setup_data.sh`
Complete setup script that runs the entire data pipeline.

**Features:**
- Creates Python virtual environment
- Installs dependencies
- Generates data files
- Seeds the database
- Copies database to Tauri directory

**Usage:**
```bash
./scripts/setup_data.sh
```

## Data Structure

### Items (`data/items.json`)
```json
{
  "id": 16,
  "name": "Wild Horseradish",
  "description": "A spicy root found in the spring.",
  "category": "Foraging",
  "sell_price": 35,
  "energy": 62,
  "health": 27
}
```

### Bundles (`data/bundles.json`)
```json
{
  "id": 1,
  "name": "Spring Foraging Bundle",
  "room": "Crafts Room",
  "reward": "30 Spring Seeds",
  "items": [
    {"item_id": 16, "quantity": 1},
    {"item_id": 18, "quantity": 1}
  ]
}
```

## Database Schema

The scripts populate these tables:

- **items**: Item catalog with stats and descriptions
- **bundles**: Community Center bundles with rewards
- **bundle_items**: Many-to-many relationship between bundles and items
- **user_progress**: Tracks completion status (empty initially)

## Requirements

- Python 3.7+
- Virtual environment (recommended)
- SQLite database with proper schema (run migrations first)

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
```

## Quick Start

1. Ensure your database is set up:
   ```bash
   sqlx migrate run
   ```

2. Run the complete setup:
   ```bash
   ./scripts/setup_data.sh
   ```

3. Verify the data:
   ```bash
   sqlite3 junimo.db "SELECT COUNT(*) FROM items; SELECT COUNT(*) FROM bundles;"
   ```

## Troubleshooting

**Virtual Environment Issues:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r scripts/requirements.txt
```

**Database Permission Issues:**
```bash
chmod 644 junimo.db
```

**Missing Dependencies:**
```bash
pip install --upgrade pip
pip install -r scripts/requirements.txt
```

## Data Sources

The item and bundle data is based on:
- Official Stardew Valley game data
- Stardew Valley Wiki (stardewvalleywiki.com)
- Community-verified information

All data is accurate as of Stardew Valley version 1.6+.