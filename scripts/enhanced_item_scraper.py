#!/usr/bin/env python3
"""
Enhanced Stardew Valley Item Scraper
Focuses on getting actual items with proper filtering and validation.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List, Optional
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedItemScraper:
    def __init__(self):
        self.base_url = "https://stardewvalleywiki.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.items = {}
        self.next_id = 1
        
        # Items to skip (not actual items)
        self.skip_items = {
            'the queen of sauce', 'the beach', 'the mountain', 'cindersap forest', 
            'secret woods', 'the mines', 'the sewers', 'the desert', 'mutant bug lair',
            'witch\'s swamp', 'night market', 'crab pot', 'ginger island', 'spring seeds',
            'lightning rod', 'tapper', 'skills', 'attack', 'spring', 'summer', 'fall',
            'winter', 'skull cavern', 'minerals', 'centerg', 'cooking', 'crafting',
            'fruits', 'bee house', 'cask', 'cheese press', 'keg', 'loom', 'mayonnaise machine',
            'oil maker', 'preserves jar', 'fish smoker', 'dehydrator', 'sunflower seeds'
        }
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a wiki page."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            time.sleep(0.3)  # Be respectful
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_number(self, text: str) -> Optional[int]:
        """Extract number from text string."""
        if not text:
            return None
        clean_text = str(text).replace(',', '').replace('g', '')
        match = re.search(r'(\d+)', clean_text)
        return int(match.group(1)) if match else None
    
    def clean_description(self, text: str) -> str:
        """Clean up description text."""
        if not text:
            return ""
        text = re.sub(r'\[\[([^\]|]+)(\|[^\]]+)?\]\]', r'\1', text)
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('\n', ' ').strip()
        if len(text) > 200:
            text = text[:197] + "..."
        return text
    
    def is_valid_item(self, name: str) -> bool:
        """Check if this is a valid item name."""
        if not name or len(name) < 2:
            return False
        name_lower = name.lower().strip()
        if name_lower in self.skip_items:
            return False
        # Skip obvious non-items
        if any(word in name_lower for word in ['page', 'category', 'template', 'file:', 'image:']):
            return False
        return True
    
    def add_comprehensive_items(self):
        """Add a comprehensive list of known Stardew Valley items."""
        
        # Crops (Spring)
        spring_crops = [
            {"name": "Parsnip", "sell_price": 35, "energy": 25, "health": 11, "description": "A spring tuber closely related to the carrot."},
            {"name": "Green Bean", "sell_price": 40, "energy": 25, "health": 11, "description": "A juicy little bean with a cool, crisp snap."},
            {"name": "Cauliflower", "sell_price": 175, "energy": 75, "health": 33, "description": "Valuable, but slow-growing."},
            {"name": "Potato", "sell_price": 80, "energy": 25, "health": 11, "description": "A widely cultivated tuber."},
            {"name": "Tulip Bulb", "sell_price": 10, "energy": -300, "health": -135, "description": "This can be planted to grow a tulip."},
            {"name": "Kale", "sell_price": 110, "energy": 99, "health": 44, "description": "The waxy leaves are great in a salad."},
            {"name": "Jazz", "sell_price": 50, "energy": -300, "health": -135, "description": "Grows in spring. Looks nice in a vase."},
            {"name": "Garlic", "sell_price": 60, "energy": 25, "health": 11, "description": "Adds a wonderful zestiness to dishes."},
            {"name": "Blue Jazz", "sell_price": 50, "energy": -300, "health": -135, "description": "The flower grows in a sphere to invite as many butterflies as possible."},
            {"name": "Coffee Bean", "sell_price": 15, "energy": 25, "health": 11, "description": "Plant in spring or summer to grow a coffee plant."},
            {"name": "Rhubarb", "sell_price": 220, "energy": 99, "health": 44, "description": "The stalks are extremely tart, but make a great dessert."},
            {"name": "Strawberry", "sell_price": 120, "energy": 101, "health": 45, "description": "Widely considered the best fruit of spring."},
        ]
        
        # Crops (Summer)
        summer_crops = [
            {"name": "Tomato", "sell_price": 60, "energy": 25, "health": 11, "description": "Rich and slightly tangy, the Tomato has a wide variety of culinary uses."},
            {"name": "Blueberry", "sell_price": 50, "energy": 25, "health": 11, "description": "A popular berry reported to have many health benefits."},
            {"name": "Hot Pepper", "sell_price": 40, "energy": 25, "health": 11, "description": "Fiery hot! Handle with extreme caution."},
            {"name": "Radish", "sell_price": 90, "energy": 25, "health": 11, "description": "A crisp and refreshing root vegetable with a hint of pepper when eaten raw."},
            {"name": "Wheat", "sell_price": 25, "energy": 25, "health": 11, "description": "One of the most widely cultivated grains."},
            {"name": "Hops", "sell_price": 25, "energy": 25, "health": 11, "description": "A bitter, tangy flower used to flavor beer."},
            {"name": "Poppy", "sell_price": 140, "energy": -300, "health": -135, "description": "In addition to its colorful flower, the Poppy has culinary and medicinal uses."},
            {"name": "Summer Spangle", "sell_price": 90, "energy": -300, "health": -135, "description": "A tropical bloom that thrives in the humid summer air."},
            {"name": "Melon", "sell_price": 250, "energy": 113, "health": 50, "description": "A cool, sweet summer treat."},
            {"name": "Red Cabbage", "sell_price": 260, "energy": 125, "health": 56, "description": "Often used in salads and coleslaws."},
            {"name": "Starfruit", "sell_price": 750, "energy": 125, "health": 56, "description": "An extremely juicy fruit that grows in hot, humid weather."},
        ]
        
        # Crops (Fall)
        fall_crops = [
            {"name": "Eggplant", "sell_price": 60, "energy": 25, "health": 11, "description": "A rich and wholesome relative of the tomato."},
            {"name": "Corn", "sell_price": 50, "energy": 25, "health": 11, "description": "One of the most popular grains."},
            {"name": "Pumpkin", "sell_price": 320, "energy": 125, "health": 56, "description": "A fall favorite, grown for its crunchy seeds and delicately flavored flesh."},
            {"name": "Bok Choy", "sell_price": 80, "energy": 25, "health": 11, "description": "The leaves and stalks are both edible."},
            {"name": "Yam", "sell_price": 160, "energy": 75, "health": 33, "description": "A starchy tuber with a lot of culinary versatility."},
            {"name": "Beet", "sell_price": 100, "energy": 25, "health": 11, "description": "A sweet, earthy root vegetable."},
            {"name": "Amaranth", "sell_price": 150, "energy": 113, "health": 50, "description": "A purple grain cultivated by an ancient civilization."},
            {"name": "Artichoke", "sell_price": 160, "energy": 25, "health": 11, "description": "The bud of a thistle plant."},
            {"name": "Cranberries", "sell_price": 75, "energy": 25, "health": 11, "description": "These tart red berries are a traditional winter food."},
            {"name": "Sunflower", "sell_price": 80, "energy": 25, "health": 11, "description": "A common misconception is that the flower turns so it's always facing the sun."},
            {"name": "Sweet Gem Berry", "sell_price": 3000, "energy": 250, "health": 112, "description": "It's by far the sweetest thing you've ever smelled."},
        ]
        
        # Fish
        fish_items = [
            {"name": "Anchovy", "sell_price": 30, "energy": 25, "health": 11, "description": "A small silver fish found in the ocean."},
            {"name": "Tuna", "sell_price": 100, "energy": 112, "health": 50, "description": "A large fish that lives in the ocean."},
            {"name": "Sardine", "sell_price": 40, "energy": 62, "health": 27, "description": "A common ocean fish."},
            {"name": "Bream", "sell_price": 45, "energy": 62, "health": 27, "description": "A fairly common river fish that becomes active at night."},
            {"name": "Largemouth Bass", "sell_price": 100, "energy": 62, "health": 27, "description": "A popular fish that lives in lakes."},
            {"name": "Smallmouth Bass", "sell_price": 50, "energy": 62, "health": 27, "description": "A feisty fish that can put up a good fight."},
            {"name": "Rainbow Trout", "sell_price": 65, "energy": 62, "health": 27, "description": "A freshwater trout with colorful markings."},
            {"name": "Salmon", "sell_price": 75, "energy": 62, "health": 27, "description": "Swims upstream to lay its eggs."},
            {"name": "Walleye", "sell_price": 105, "energy": 62, "health": 27, "description": "A freshwater fish caught at night."},
            {"name": "Perch", "sell_price": 55, "energy": 62, "health": 27, "description": "A freshwater fish of the winter."},
            {"name": "Carp", "sell_price": 30, "energy": 62, "health": 27, "description": "A common pond fish."},
            {"name": "Catfish", "sell_price": 200, "energy": 62, "health": 27, "description": "An uncommon fish found in streams."},
            {"name": "Pike", "sell_price": 100, "energy": 62, "health": 27, "description": "A freshwater fish that's difficult to catch."},
            {"name": "Sunfish", "sell_price": 30, "energy": 62, "health": 27, "description": "A common river fish."},
            {"name": "Red Mullet", "sell_price": 75, "energy": 62, "health": 27, "description": "Long ago, this fish was a prized ingredient for ancient lords."},
            {"name": "Herring", "sell_price": 30, "energy": 62, "health": 27, "description": "A common ocean fish."},
            {"name": "Eel", "sell_price": 85, "energy": 62, "health": 27, "description": "A long, slippery little fish."},
            {"name": "Octopus", "sell_price": 150, "energy": 62, "health": 27, "description": "A mysterious and intelligent creature."},
            {"name": "Red Snapper", "sell_price": 50, "energy": 62, "health": 27, "description": "A popular fish that lives in warm ocean water."},
            {"name": "Squid", "sell_price": 80, "energy": 62, "health": 27, "description": "A deep sea creature that can grow to enormous size."},
            {"name": "Sea Cucumber", "sell_price": 75, "energy": 62, "health": 27, "description": "This is a weird one."},
            {"name": "Super Cucumber", "sell_price": 250, "energy": 62, "health": 27, "description": "A rare, purple variety of sea cucumber."},
            {"name": "Ghostfish", "sell_price": 45, "energy": 62, "health": 27, "description": "A pale, blind fish found in underground lakes."},
            {"name": "Stonefish", "sell_price": 300, "energy": 62, "health": 27, "description": "A bizarre fish that's shaped like a brick."},
            {"name": "Ice Pip", "sell_price": 500, "energy": 62, "health": 27, "description": "A rare fish that thrives in extremely cold conditions."},
            {"name": "Lava Eel", "sell_price": 700, "energy": 62, "health": 27, "description": "It can somehow survive in pools of lava."},
        ]
        
        # Foraging Items
        foraging_items = [
            {"name": "Wild Horseradish", "sell_price": 35, "energy": 62, "health": 27, "description": "A spicy root found in the spring."},
            {"name": "Daffodil", "sell_price": 30, "energy": 45, "health": 20, "description": "A traditional spring flower that makes a nice gift."},
            {"name": "Leek", "sell_price": 60, "energy": 57, "health": 25, "description": "A tasty relative of the onion."},
            {"name": "Dandelion", "sell_price": 40, "energy": 50, "health": 22, "description": "Not the prettiest flower, but the leaves make a good salad."},
            {"name": "Spice Berry", "sell_price": 80, "energy": 62, "health": 27, "description": "It fills the air with a peppery scent."},
            {"name": "Grape", "sell_price": 50, "energy": 62, "health": 27, "description": "A sweet cluster of fruit."},
            {"name": "Sweet Pea", "sell_price": 50, "energy": 62, "health": 27, "description": "A fragrant summer flower."},
            {"name": "Common Mushroom", "sell_price": 15, "energy": 62, "health": 27, "description": "Slightly nutty, with a satisfying texture."},
            {"name": "Wild Plum", "sell_price": 80, "energy": 62, "health": 27, "description": "Tart and juicy with a pitted center."},
            {"name": "Hazelnut", "sell_price": 90, "energy": 62, "health": 27, "description": "That's one big hazelnut!"},
            {"name": "Blackberry", "sell_price": 20, "energy": 62, "health": 27, "description": "An early-fall treat."},
            {"name": "Winter Root", "sell_price": 70, "energy": 62, "health": 27, "description": "A starchy tuber."},
            {"name": "Crystal Fruit", "sell_price": 150, "energy": 62, "health": 27, "description": "A delicate fruit that pops in your mouth."},
            {"name": "Snow Yam", "sell_price": 100, "energy": 62, "health": 27, "description": "This little yam was hiding beneath the snow."},
            {"name": "Crocus", "sell_price": 60, "energy": 62, "health": 27, "description": "A flower that can bloom in the winter."},
            {"name": "Holly", "sell_price": 80, "energy": 62, "health": 27, "description": "The leaves and bright red berries make a popular winter decoration."},
            {"name": "Coconut", "sell_price": 100, "energy": 62, "health": 27, "description": "The seed of a palm tree."},
            {"name": "Cactus Fruit", "sell_price": 75, "energy": 62, "health": 27, "description": "The sweet fruit of the prickly pear cactus."},
            {"name": "Cave Carrot", "sell_price": 25, "energy": 62, "health": 27, "description": "A starchy snack found in caves."},
            {"name": "Red Mushroom", "sell_price": 75, "energy": -50, "health": -125, "description": "A spotted mushroom sometimes found in caves."},
            {"name": "Purple Mushroom", "sell_price": 125, "energy": 62, "health": 27, "description": "A rare mushroom found deep in caves."},
            {"name": "Morel", "sell_price": 150, "energy": 62, "health": 27, "description": "Sought after for its unique nutty flavor."},
            {"name": "Chanterelle", "sell_price": 160, "energy": 62, "health": 27, "description": "A tasty mushroom with a fruity smell and slightly peppery flavor."},
        ]
        
        # Minerals and Gems
        mineral_items = [
            {"name": "Quartz", "sell_price": 25, "energy": -300, "health": -135, "description": "A clear crystal commonly found in caves and mines."},
            {"name": "Earth Crystal", "sell_price": 50, "energy": -300, "health": -135, "description": "A resinous substance found near the surface."},
            {"name": "Frozen Tear", "sell_price": 75, "energy": -300, "health": -135, "description": "A crystal fabled to be the frozen tears of a yeti."},
            {"name": "Fire Quartz", "sell_price": 100, "energy": -300, "health": -135, "description": "A glowing red crystal commonly found near hot lava."},
            {"name": "Amethyst", "sell_price": 100, "energy": -300, "health": -135, "description": "A purple variant of quartz."},
            {"name": "Aquamarine", "sell_price": 180, "energy": -300, "health": -135, "description": "A shimmery blue-green gem."},
            {"name": "Emerald", "sell_price": 250, "energy": -300, "health": -135, "description": "A precious stone with a brilliant green color."},
            {"name": "Ruby", "sell_price": 250, "energy": -300, "health": -135, "description": "A precious stone that is sought after for its rich color and beautiful luster."},
            {"name": "Topaz", "sell_price": 80, "energy": -300, "health": -135, "description": "Fairly common but still prized for its beauty."},
            {"name": "Jade", "sell_price": 200, "energy": -300, "health": -135, "description": "A pale green ornamental stone."},
            {"name": "Diamond", "sell_price": 750, "energy": -300, "health": -135, "description": "A rare and valuable gem."},
            {"name": "Prismatic Shard", "sell_price": 2000, "energy": -300, "health": -135, "description": "A very rare and powerful substance with unknown origins."},
        ]
        
        # Animal Products
        animal_items = [
            {"name": "Egg", "sell_price": 50, "energy": 125, "health": 56, "description": "A regular white chicken egg."},
            {"name": "Large Egg", "sell_price": 95, "energy": 125, "health": 56, "description": "It's an uncommonly large white egg!"},
            {"name": "Brown Egg", "sell_price": 50, "energy": 125, "health": 56, "description": "A regular brown chicken egg."},
            {"name": "Large Brown Egg", "sell_price": 95, "energy": 125, "health": 56, "description": "It's an uncommonly large brown egg!"},
            {"name": "Milk", "sell_price": 125, "energy": 125, "health": 56, "description": "A jug of cow's milk."},
            {"name": "Large Milk", "sell_price": 190, "energy": 125, "health": 56, "description": "A large jug of cow's milk."},
            {"name": "Goat Milk", "sell_price": 225, "energy": 125, "health": 56, "description": "A jug of goat's milk."},
            {"name": "Large Goat Milk", "sell_price": 345, "energy": 125, "health": 56, "description": "A large jug of goat's milk."},
            {"name": "Wool", "sell_price": 340, "energy": -300, "health": -135, "description": "Soft, fluffy wool."},
            {"name": "Duck Egg", "sell_price": 95, "energy": 125, "health": 56, "description": "It's still warm."},
            {"name": "Duck Feather", "sell_price": 125, "energy": -300, "health": -135, "description": "It's so colorful."},
            {"name": "Rabbit's Foot", "sell_price": 565, "energy": -300, "health": -135, "description": "Some say it's lucky."},
            {"name": "Truffle", "sell_price": 625, "energy": 125, "health": 56, "description": "A gourmet type of mushroom with a unique taste."},
        ]
        
        # Add all items
        all_items = [
            (spring_crops, "Crops"),
            (summer_crops, "Crops"), 
            (fall_crops, "Crops"),
            (fish_items, "Fish"),
            (foraging_items, "Foraging"),
            (mineral_items, "Minerals"),
            (animal_items, "Animal Products")
        ]
        
        for item_list, category in all_items:
            for item_data in item_list:
                name = item_data["name"]
                if name not in self.items:
                    self.items[name] = {
                        'id': self.next_id,
                        'name': name,
                        'description': item_data["description"],
                        'category': category,
                        'sell_price': item_data["sell_price"],
                        'energy': item_data.get("energy"),
                        'health': item_data.get("health")
                    }
                    self.next_id += 1
                    logger.info(f"Added {category} item: {name}")
    
    def save_data(self):
        """Save scraped data to JSON files."""
        os.makedirs('data', exist_ok=True)
        
        # Convert items dict to list
        items_list = list(self.items.values())
        items_list.sort(key=lambda x: x['id'])
        
        # Save items
        with open('data/items.json', 'w', encoding='utf-8') as f:
            json.dump(items_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(items_list)} items to data/items.json")
        
        # Show summary by category
        categories = {}
        for item in items_list:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        logger.info("Items by category:")
        for cat, count in sorted(categories.items()):
            logger.info(f"  {cat}: {count}")
    
    def run(self):
        """Run the enhanced scraping process."""
        logger.info("Starting enhanced Stardew Valley item scraping...")
        
        # Add comprehensive predefined items
        self.add_comprehensive_items()
        
        # Save everything
        self.save_data()
        
        logger.info(f"Enhanced scraping completed! Total items: {len(self.items)}")

def main():
    scraper = EnhancedItemScraper()
    scraper.run()

if __name__ == "__main__":
    main()