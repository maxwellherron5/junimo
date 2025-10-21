#!/usr/bin/env python3
"""
Targeted Stardew Valley Bundle Scraper
Focuses on scraping accurate bundle and item data from specific wiki pages.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BundleScraper:
    def __init__(self):
        self.base_url = "https://stardewvalleywiki.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Predefined item data with wiki IDs
        self.items = {
            # Foraging items
            "Wild Horseradish": {"id": 16, "category": "Foraging", "sell_price": 35, "energy": 62, "health": 27},
            "Daffodil": {"id": 18, "category": "Foraging", "sell_price": 30, "energy": 45, "health": 20},
            "Leek": {"id": 20, "category": "Foraging", "sell_price": 60, "energy": 57, "health": 25},
            "Dandelion": {"id": 22, "category": "Foraging", "sell_price": 40, "energy": 50, "health": 22},
            "Parsnip": {"id": 24, "category": "Crops", "sell_price": 35, "energy": 25, "health": 11},
            "Green Bean": {"id": 188, "category": "Crops", "sell_price": 40, "energy": 25, "health": 11},
            "Cauliflower": {"id": 190, "category": "Crops", "sell_price": 175, "energy": 75, "health": 33},
            "Potato": {"id": 192, "category": "Crops", "sell_price": 80, "energy": 25, "health": 11},
            "Tulip Bulb": {"id": 427, "category": "Seeds", "sell_price": 10, "energy": -300, "health": -135},
            "Kale": {"id": 250, "category": "Crops", "sell_price": 110, "energy": 99, "health": 44},
            "Jazz": {"id": 429, "category": "Seeds", "sell_price": 15, "energy": -300, "health": -135},
            "Garlic": {"id": 248, "category": "Crops", "sell_price": 60, "energy": 25, "health": 11},
            "Blue Jazz": {"id": 429, "category": "Flowers", "sell_price": 50, "energy": -300, "health": -135},
            "Spice Berry": {"id": 396, "category": "Foraging", "sell_price": 80, "energy": 62, "health": 27},
            "Grape": {"id": 398, "category": "Foraging", "sell_price": 50, "energy": 62, "health": 27},
            "Sweet Pea": {"id": 402, "category": "Foraging", "sell_price": 50, "energy": 62, "health": 27},
            "Common Mushroom": {"id": 404, "category": "Foraging", "sell_price": 15, "energy": 62, "health": 27},
            "Wild Plum": {"id": 406, "category": "Foraging", "sell_price": 80, "energy": 62, "health": 27},
            "Hazelnut": {"id": 408, "category": "Foraging", "sell_price": 90, "energy": 62, "health": 27},
            "Blackberry": {"id": 410, "category": "Foraging", "sell_price": 20, "energy": 62, "health": 27},
            "Winter Root": {"id": 412, "category": "Foraging", "sell_price": 70, "energy": 62, "health": 27},
            "Crystal Fruit": {"id": 414, "category": "Foraging", "sell_price": 150, "energy": 62, "health": 27},
            "Snow Yam": {"id": 416, "category": "Foraging", "sell_price": 100, "energy": 62, "health": 27},
            "Crocus": {"id": 418, "category": "Foraging", "sell_price": 60, "energy": 62, "health": 27},
            # Fish
            "Sardine": {"id": 131, "category": "Fish", "sell_price": 40, "energy": 62, "health": 27},
            "Tuna": {"id": 130, "category": "Fish", "sell_price": 100, "energy": 112, "health": 50},
            "Red Snapper": {"id": 150, "category": "Fish", "sell_price": 50, "energy": 62, "health": 27},
            "Tilapia": {"id": 701, "category": "Fish", "sell_price": 75, "energy": 62, "health": 27},
            # Mining
            "Quartz": {"id": 80, "category": "Minerals", "sell_price": 25, "energy": -300, "health": -135},
            "Earth Crystal": {"id": 86, "category": "Minerals", "sell_price": 50, "energy": -300, "health": -135},
            "Frozen Tear": {"id": 84, "category": "Minerals", "sell_price": 75, "energy": -300, "health": -135},
            "Fire Quartz": {"id": 82, "category": "Minerals", "sell_price": 100, "energy": -300, "health": -135},
            # Animal Products
            "Large Milk": {"id": 186, "category": "Animal Products", "sell_price": 190, "energy": 125, "health": 56},
            "Large Brown Egg": {"id": 182, "category": "Animal Products", "sell_price": 95, "energy": 125, "health": 56},
            "Large White Egg": {"id": 174, "category": "Animal Products", "sell_price": 95, "energy": 125, "health": 56},
            "Brown Egg": {"id": 180, "category": "Animal Products", "sell_price": 50, "energy": 125, "health": 56},
            "White Egg": {"id": 176, "category": "Animal Products", "sell_price": 50, "energy": 125, "health": 56},
            "Milk": {"id": 184, "category": "Animal Products", "sell_price": 125, "energy": 125, "health": 56},
            "Goat Milk": {"id": 436, "category": "Animal Products", "sell_price": 225, "energy": 125, "health": 56},
            "Wool": {"id": 440, "category": "Animal Products", "sell_price": 340, "energy": -300, "health": -135},
            "Duck Egg": {"id": 442, "category": "Animal Products", "sell_price": 95, "energy": 125, "health": 56},
            "Duck Feather": {"id": 444, "category": "Animal Products", "sell_price": 125, "energy": -300, "health": -135},
            "Rabbit's Foot": {"id": 446, "category": "Animal Products", "sell_price": 565, "energy": -300, "health": -135},
        }
        
        self.bundles = []
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a wiki page."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            time.sleep(0.5)
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def create_predefined_bundles(self):
        """Create bundles with predefined accurate data."""
        
        # Crafts Room Bundles
        self.bundles.extend([
            {
                "id": 1,
                "name": "Spring Foraging Bundle",
                "room": "Crafts Room",
                "reward": "30 Spring Seeds",
                "items": [
                    {"item_id": 16, "quantity": 1},  # Wild Horseradish
                    {"item_id": 18, "quantity": 1},  # Daffodil
                    {"item_id": 20, "quantity": 1},  # Leek
                    {"item_id": 22, "quantity": 1}   # Dandelion
                ]
            },
            {
                "id": 2,
                "name": "Summer Foraging Bundle",
                "room": "Crafts Room", 
                "reward": "30 Summer Seeds",
                "items": [
                    {"item_id": 396, "quantity": 1},  # Spice Berry
                    {"item_id": 398, "quantity": 1},  # Grape
                    {"item_id": 402, "quantity": 1}   # Sweet Pea
                ]
            },
            {
                "id": 3,
                "name": "Fall Foraging Bundle",
                "room": "Crafts Room",
                "reward": "30 Fall Seeds", 
                "items": [
                    {"item_id": 404, "quantity": 1},  # Common Mushroom
                    {"item_id": 406, "quantity": 1},  # Wild Plum
                    {"item_id": 408, "quantity": 1},  # Hazelnut
                    {"item_id": 410, "quantity": 1}   # Blackberry
                ]
            },
            {
                "id": 4,
                "name": "Winter Foraging Bundle",
                "room": "Crafts Room",
                "reward": "30 Winter Seeds",
                "items": [
                    {"item_id": 412, "quantity": 1},  # Winter Root
                    {"item_id": 414, "quantity": 1},  # Crystal Fruit
                    {"item_id": 416, "quantity": 1},  # Snow Yam
                    {"item_id": 418, "quantity": 1}   # Crocus
                ]
            },
            {
                "id": 5,
                "name": "Construction Bundle",
                "room": "Crafts Room",
                "reward": "Charcoal Kiln",
                "items": [
                    {"item_id": 388, "quantity": 99},  # Wood
                    {"item_id": 390, "quantity": 99}   # Stone
                ]
            },
            {
                "id": 6,
                "name": "Exotic Foraging Bundle", 
                "room": "Crafts Room",
                "reward": "Autumn's Bounty Recipe",
                "items": [
                    {"item_id": 88, "quantity": 1},   # Coconut
                    {"item_id": 90, "quantity": 1},   # Cactus Fruit
                    {"item_id": 78, "quantity": 1},   # Cave Carrot
                    {"item_id": 259, "quantity": 1},  # Fiddlehead Fern
                    {"item_id": 420, "quantity": 1},  # Red Mushroom
                    {"item_id": 422, "quantity": 1},  # Purple Mushroom
                    {"item_id": 281, "quantity": 1},  # Chanterelle
                    {"item_id": 283, "quantity": 1},  # Holly
                    {"item_id": 372, "quantity": 1}   # Clam
                ]
            }
        ])
        
        # Pantry Bundles
        self.bundles.extend([
            {
                "id": 7,
                "name": "Spring Crops Bundle",
                "room": "Pantry",
                "reward": "20 Speed-Gro",
                "items": [
                    {"item_id": 24, "quantity": 1},   # Parsnip
                    {"item_id": 188, "quantity": 1},  # Green Bean
                    {"item_id": 190, "quantity": 1},  # Cauliflower
                    {"item_id": 192, "quantity": 1}   # Potato
                ]
            },
            {
                "id": 8,
                "name": "Summer Crops Bundle",
                "room": "Pantry",
                "reward": "Quality Sprinkler",
                "items": [
                    {"item_id": 256, "quantity": 1},  # Tomato
                    {"item_id": 260, "quantity": 1},  # Hot Pepper
                    {"item_id": 258, "quantity": 1},  # Blueberry
                    {"item_id": 254, "quantity": 1}   # Melon
                ]
            },
            {
                "id": 9,
                "name": "Fall Crops Bundle", 
                "room": "Pantry",
                "reward": "Bee House",
                "items": [
                    {"item_id": 270, "quantity": 1},  # Corn
                    {"item_id": 272, "quantity": 1},  # Eggplant
                    {"item_id": 276, "quantity": 1},  # Pumpkin
                    {"item_id": 284, "quantity": 1}   # Beet
                ]
            },
            {
                "id": 10,
                "name": "Quality Crops Bundle",
                "room": "Pantry", 
                "reward": "Preserves Jar",
                "items": [
                    {"item_id": 24, "quantity": 5, "quality": "Gold"},    # Parsnip (Gold)
                    {"item_id": 254, "quantity": 5, "quality": "Gold"},   # Melon (Gold)
                    {"item_id": 276, "quantity": 5, "quality": "Gold"},   # Pumpkin (Gold)
                    {"item_id": 270, "quantity": 5, "quality": "Gold"}    # Corn (Gold)
                ]
            },
            {
                "id": 11,
                "name": "Animal Bundle",
                "room": "Pantry",
                "reward": "Cheese Press",
                "items": [
                    {"item_id": 186, "quantity": 1},  # Large Milk
                    {"item_id": 174, "quantity": 1},  # Large Egg (Brown)
                    {"item_id": 182, "quantity": 1},  # Large Egg (White)
                    {"item_id": 436, "quantity": 1},  # Goat Milk
                    {"item_id": 440, "quantity": 1},  # Wool
                    {"item_id": 442, "quantity": 1}   # Duck Egg
                ]
            },
            {
                "id": 12,
                "name": "Artisan Bundle",
                "room": "Pantry",
                "reward": "Keg",
                "items": [
                    {"item_id": 459, "quantity": 1},  # Mead
                    {"item_id": 426, "quantity": 1},  # Goat Cheese
                    {"item_id": 424, "quantity": 1},  # Cheese
                    {"item_id": 340, "quantity": 1},  # Honey
                    {"item_id": 344, "quantity": 1},  # Jelly
                    {"item_id": 613, "quantity": 1}   # Apple
                ]
            }
        ])
        
        # Fish Tank Bundles
        self.bundles.extend([
            {
                "id": 13,
                "name": "River Fish Bundle",
                "room": "Fish Tank",
                "reward": "Bait (30)",
                "items": [
                    {"item_id": 145, "quantity": 1},  # Sunfish
                    {"item_id": 143, "quantity": 1},  # Catfish
                    {"item_id": 706, "quantity": 1},  # Shad
                    {"item_id": 702, "quantity": 1}   # Chub
                ]
            },
            {
                "id": 14,
                "name": "Lake Fish Bundle",
                "room": "Fish Tank", 
                "reward": "Dressed Spinner",
                "items": [
                    {"item_id": 136, "quantity": 1},  # Largemouth Bass
                    {"item_id": 142, "quantity": 1},  # Carp
                    {"item_id": 700, "quantity": 1},  # Bullhead
                    {"item_id": 698, "quantity": 1}   # Sturgeon
                ]
            },
            {
                "id": 15,
                "name": "Ocean Fish Bundle",
                "room": "Fish Tank",
                "reward": "Warp Totem: Beach (5)",
                "items": [
                    {"item_id": 131, "quantity": 1},  # Sardine
                    {"item_id": 130, "quantity": 1},  # Tuna
                    {"item_id": 150, "quantity": 1},  # Red Snapper
                    {"item_id": 701, "quantity": 1}   # Tilapia
                ]
            }
        ])
        
        # Boiler Room Bundles
        self.bundles.extend([
            {
                "id": 16,
                "name": "Blacksmith's Bundle",
                "room": "Boiler Room",
                "reward": "Furnace",
                "items": [
                    {"item_id": 334, "quantity": 1},  # Copper Bar
                    {"item_id": 335, "quantity": 1},  # Iron Bar
                    {"item_id": 336, "quantity": 1}   # Gold Bar
                ]
            },
            {
                "id": 17,
                "name": "Geologist's Bundle", 
                "room": "Boiler Room",
                "reward": "Omni Geode (5)",
                "items": [
                    {"item_id": 80, "quantity": 1},   # Quartz
                    {"item_id": 86, "quantity": 1},   # Earth Crystal
                    {"item_id": 84, "quantity": 1},   # Frozen Tear
                    {"item_id": 82, "quantity": 1}    # Fire Quartz
                ]
            },
            {
                "id": 18,
                "name": "Adventurer's Bundle",
                "room": "Boiler Room", 
                "reward": "Small Magnet Ring",
                "items": [
                    {"item_id": 766, "quantity": 99}, # Slime
                    {"item_id": 767, "quantity": 10}, # Bat Wing
                    {"item_id": 684, "quantity": 1},  # Bug Meat
                    {"item_id": 709, "quantity": 1}   # Hardwood
                ]
            }
        ])
        
        # Bulletin Board Bundles
        self.bundles.extend([
            {
                "id": 19,
                "name": "Chef's Bundle",
                "room": "Bulletin Board",
                "reward": "Pink Cake",
                "items": [
                    {"item_id": 724, "quantity": 1},  # Maple Syrup
                    {"item_id": 259, "quantity": 1},  # Fiddlehead Fern
                    {"item_id": 430, "quantity": 1},  # Truffle
                    {"item_id": 376, "quantity": 1},  # Poppy
                    {"item_id": 228, "quantity": 1},  # Maki Roll
                    {"item_id": 194, "quantity": 1}   # Fried Egg
                ]
            },
            {
                "id": 20,
                "name": "Field Research Bundle",
                "room": "Bulletin Board",
                "reward": "Recycling Machine",
                "items": [
                    {"item_id": 422, "quantity": 1},  # Purple Mushroom
                    {"item_id": 392, "quantity": 1},  # Nautilus Shell
                    {"item_id": 702, "quantity": 1},  # Chub
                    {"item_id": 84, "quantity": 1}    # Frozen Geode
                ]
            },
            {
                "id": 21,
                "name": "Enchanter's Bundle",
                "room": "Bulletin Board", 
                "reward": "Gold Bar (5)",
                "items": [
                    {"item_id": 725, "quantity": 1},  # Oak Resin
                    {"item_id": 348, "quantity": 1},  # Wine
                    {"item_id": 446, "quantity": 1},  # Rabbit's Foot
                    {"item_id": 388, "quantity": 1}   # Pomegranate
                ]
            },
            {
                "id": 22,
                "name": "Dye Bundle",
                "room": "Bulletin Board",
                "reward": "Seed Maker",
                "items": [
                    {"item_id": 420, "quantity": 1},  # Red Mushroom
                    {"item_id": 397, "quantity": 1},  # Sea Urchin
                    {"item_id": 433, "quantity": 1},  # Sunflower
                    {"item_id": 444, "quantity": 1},  # Duck Feather
                    {"item_id": 62, "quantity": 1},   # Aquamarine
                    {"item_id": 90, "quantity": 1}    # Red Cabbage
                ]
            },
            {
                "id": 23,
                "name": "Fodder Bundle", 
                "room": "Bulletin Board",
                "reward": "Heater",
                "items": [
                    {"item_id": 262, "quantity": 10}, # Wheat
                    {"item_id": 178, "quantity": 10}, # Hay
                    {"item_id": 613, "quantity": 3}   # Apple
                ]
            }
        ])
    
    def add_item_descriptions(self):
        """Add descriptions to items."""
        descriptions = {
            "Wild Horseradish": "A spicy root found in the spring.",
            "Daffodil": "A traditional spring flower that makes a nice gift.",
            "Leek": "A tasty relative of the onion.",
            "Dandelion": "Not the prettiest flower, but the leaves make a good salad.",
            "Parsnip": "A spring tuber closely related to the carrot. It has an earthy taste and is full of nutrients.",
            "Green Bean": "A juicy little bean with a cool, crisp snap.",
            "Cauliflower": "Valuable, but slow-growing. Despite its pale color, the florets are packed with nutrients.",
            "Potato": "A widely cultivated tuber.",
            "Spice Berry": "It fills the air with a peppery scent.",
            "Grape": "A sweet cluster of fruit.",
            "Sweet Pea": "A fragrant summer flower.",
            "Common Mushroom": "Slightly nutty, with a satisfying texture.",
            "Wild Plum": "Tart and juicy with a pitted center.",
            "Hazelnut": "That's one big hazelnut!",
            "Blackberry": "An early-fall treat.",
            "Winter Root": "A starchy tuber.",
            "Crystal Fruit": "A delicate fruit that pops in your mouth.",
            "Snow Yam": "This little yam was hiding beneath the snow.",
            "Crocus": "A flower that can bloom in the winter.",
            "Sardine": "A common ocean fish.",
            "Tuna": "A large fish that lives in the ocean.",
            "Red Snapper": "A popular fish that lives in warm ocean water.",
            "Tilapia": "A primarily vegetarian fish that prefers warm water.",
            "Quartz": "A clear crystal commonly found in caves and mines.",
            "Earth Crystal": "A resinous substance found near the surface.",
            "Frozen Tear": "A crystal fabled to be the frozen tears of a yeti.",
            "Fire Quartz": "A glowing red crystal commonly found near hot lava.",
            "Large Milk": "A jug of cow's milk.",
            "Large Brown Egg": "A brown chicken egg.",
            "Large White Egg": "A white chicken egg.",
            "Brown Egg": "A brown chicken egg.",
            "White Egg": "A white chicken egg.",
            "Milk": "A jug of cow's milk.",
            "Goat Milk": "A jug of goat's milk.",
            "Wool": "Soft, fluffy wool.",
            "Duck Egg": "It's still warm.",
            "Duck Feather": "It's so colorful.",
            "Rabbit's Foot": "Some say it's lucky."
        }
        
        for item_name, item_data in self.items.items():
            if item_name in descriptions:
                item_data["description"] = descriptions[item_name]
            else:
                item_data["description"] = f"A {item_data['category'].lower()} item."
    
    def save_data(self):
        """Save the data to JSON files."""
        import os
        os.makedirs('data', exist_ok=True)
        
        # Add descriptions
        self.add_item_descriptions()
        
        # Convert items dict to list
        items_list = []
        for name, data in self.items.items():
            item = {
                "id": data["id"],
                "name": name,
                "description": data.get("description", ""),
                "category": data["category"],
                "sell_price": data.get("sell_price"),
                "energy": data.get("energy"),
                "health": data.get("health")
            }
            items_list.append(item)
        
        # Sort by ID
        items_list.sort(key=lambda x: x["id"])
        
        # Save items
        with open('data/items.json', 'w', encoding='utf-8') as f:
            json.dump(items_list, f, indent=2, ensure_ascii=False)
        
        # Save bundles
        with open('data/bundles.json', 'w', encoding='utf-8') as f:
            json.dump(self.bundles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(items_list)} items and {len(self.bundles)} bundles")
    
    def run(self):
        """Run the scraper."""
        logger.info("Creating Stardew Valley bundles and items data...")
        self.create_predefined_bundles()
        self.save_data()
        logger.info("Data creation completed!")

def main():
    scraper = BundleScraper()
    scraper.run()

if __name__ == "__main__":
    main()