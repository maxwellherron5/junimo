# Junimo 🍄

A Stardew Valley companion web app that helps players browse items, track Community Center bundles, and plan villager gifts. Pure static site — no backend, no accounts, progress saved in your browser.

## Features

### **Core Features**
- **Item Database**: Browse and search 108 Stardew Valley items with detailed information
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
- **Responsive Design**: Works on desktop and mobile
- **No Account Required**: Start using immediately

## Run locally

The site is fully static — any HTTP server pointed at `docs/` works. Easiest:

```bash
cd docs
python3 -m http.server 8000
```

Then visit http://localhost:8000.

## Deploy to GitHub Pages

1. Push to GitHub.
2. In the repo, **Settings → Pages**.
3. **Source**: Deploy from a branch. **Branch**: `main` / `/docs`.
4. Save. Your site will be live at `https://<username>.github.io/<repo>/` in about a minute.

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
└── docs/                  # Static site (GitHub Pages source)
    ├── index.html         # Single-page app
    ├── main.js            # UI rendering and interaction
    ├── web-api.js         # Data layer (loads JSON, does search/filter in memory)
    ├── assets/            # Images
    └── data/              # Game data
        ├── items.json
        ├── bundles.json
        └── villagers.json
```

## Data Overview

### Items (108 total)
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

## Updating Data

Edit the JSON files in `docs/data/` and refresh — that's the whole loop. No build step, no database, no migrations.

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

---

**Made with 🍄 for the Stardew Valley community**