# Junimo 🍄

A comprehensive Stardew Valley companion web app that helps players manage items, track Community Center bundles, and plan villager gifts. Built with Rust backend and modern web frontend.

## Features

### **Core Features**
- **Item Database**: Browse and search 139+ Stardew Valley items with detailed information
- **Bundle Tracking**: View all Community Center bundles and track completion progress
- **Villager Guide**: Complete gift preferences for all 30 villagers
- **Progress Management**: Personal progress tracking stored locally in your browser

### **Enhanced Item Information**
- **Seasonal Availability**: Know when crops, fish, and foragables are available
- **Proper Nutrition**: Energy and health values only for consumable items
- **Location Data**: Where to find fish (River, Ocean, Mines)
- **Smart Filtering**: Filter items by season (Spring, Summer, Fall, Winter)

### **Complete Villager System**
- **All 30 Villagers**: Marriageable and non-marriageable characters
- **Gift Preferences**: Loved 💖, Liked 👍, Disliked 👎, Hated 💔 items
- **Personal Details**: Birthdays, locations, and character descriptions
- **461+ Gift Preferences**: Comprehensive database for perfect gift-giving

### **User Experience**
- **Local Progress**: Your progress is private and stored in your browser
- **Responsive Design**: Works perfectly on desktop and mobile
- **Fast Performance**: Rust backend with efficient SQLite database
- **No Account Required**: Start using immediately

## Quick Start

### Prerequisites
- [Rust](https://rustup.rs/) (latest stable)
- Python 3.6+ (for data setup)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/junimo.git
cd junimo
```

2. **Set up the database:**
```bash
python scripts/setup_data.py
```

3. **Run the web server:**
```bash
cd web-server
cargo run
```

4. **Open your browser:**
Visit http://localhost:3000

## Usage

### Bundle Tracking
- Navigate to the "Bundles" tab to see all Community Center bundles
- Check off items as you collect them (progress saved locally)
- View completion statistics in the "Progress" tab

### Item Search & Filtering
- Browse all items in the "Items" tab
- Search for specific items using the search bar
- Filter by season to see what's available when
- View detailed information including seasons, locations, and nutrition

### Villager Gifts
- Check the "Villagers" tab for complete gift guides
- See loved, liked, disliked, and hated items for each villager
- Plan perfect gifts for birthdays and friendship building
- Read character descriptions and find their locations

## Project Structure

```
junimo/
├── web-server/         # Rust web server
│   ├── src/           # Rust source code
│   └── static/        # Frontend assets (HTML, CSS, JS)
├── data/              # Game data (JSON files)
│   ├── items.json     # All items with enhanced data
│   ├── bundles.json   # Community Center bundles
│   └── villagers.json # Villagers and gift preferences
├── migrations/        # Database schema migrations
└── scripts/           # Data setup script
```

## Data Overview

### Items (139 total)
- **Consumables**: Proper energy/health values for crops, fish, cooked items
- **Non-consumables**: No energy/health for minerals, artifacts, etc.
- **Seasonal Items**: Spring/Summer/Fall/Winter availability
- **Location Data**: River, Ocean, Mines for fish

### Bundles (Complete Community Center)
- All rooms: Crafts, Pantry, Fish Tank, Boiler, Bulletin Board, Vault
- Accurate item requirements and quantities
- Proper reward information

### Villagers (30 total)
- **Marriageable**: 12 bachelor/bachelorettes
- **Townspeople**: All other NPCs with gift preferences
- **Complete Data**: Birthdays, locations, descriptions, gift preferences

## Development

### Running in Development
```bash
# Terminal 1: Start the web server
cd web-server
cargo run

# Terminal 2: For live development, use cargo watch
cargo install cargo-watch
cargo watch -x run
```

### Updating Data
If you need to update game data:
1. Edit JSON files in `data/` directory
2. Run the setup script: `python scripts/setup_data.py`
3. Restart the web server

### Database
- **Engine**: SQLite for simplicity and portability
- **Location**: `web-server/junimo.db`
- **Schema**: Items, bundles, villagers, and relationships

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Stardew Valley** by ConcernedApe - The amazing game this app supports
- **Stardew Valley Wiki** - Source of accurate game data
- **Rust Community** - For the excellent ecosystem and tools
- **Open Source Community** - For inspiration and best practices

---

**Made with 🍄 for the Stardew Valley community**