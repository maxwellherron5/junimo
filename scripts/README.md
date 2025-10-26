# Scripts Directory

This directory contains the data setup script for the Junimo Stardew Valley companion app.

## Main Script

### `setup_data.py`
Comprehensive script that handles all data setup for the Junimo app:

- **Items Data**: Loads items with proper energy/health values and seasonal information
- **Bundles Data**: Loads community center bundles and their required items
- **Villagers Data**: Loads all villagers with their gift preferences
- **Database Setup**: Creates all necessary tables and relationships
- **Data Validation**: Verifies data integrity and provides statistics

## Usage

Run the setup script to initialize your database:

```bash
python scripts/setup_data.py
```

This will:
1. Create the SQLite database at `web-server/junimo.db`
2. Run all necessary migrations
3. Load all game data from JSON files
4. Verify data integrity
5. Provide a summary of loaded data

## Requirements

Make sure you have Python 3.6+ installed. No additional dependencies are required as the script uses only standard library modules.

## Data Sources

The script loads data from:
- `data/items.json` - All Stardew Valley items with enhanced information
- `data/bundles.json` - Community center bundles and requirements
- `data/villagers.json` - All villagers with gift preferences

## After Setup

Once the script completes successfully, you can start the web server:

```bash
cd web-server
cargo run
```

The app will be available at http://localhost:3000

## Data Structure

### Items
- 139 unique items with proper energy/health values (only for consumables)
- Seasonal availability for crops, fish, and foragables
- Location information for fish
- Categories: Crops, Fish, Foraging, Minerals, Artisan Goods, etc.

### Bundles
- All Community Center bundles with accurate requirements
- Bundle items with proper quantities
- Room assignments and rewards

### Villagers
- All 30 villagers (marriageable and non-marriageable)
- Complete gift preferences (loved, liked, disliked, hated)
- Personal information (birthday, location, description)
- 461+ individual gift preferences across all villagers