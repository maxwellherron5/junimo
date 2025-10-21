#!/usr/bin/env python3
"""
Comprehensive Stardew Valley Item Scraper
Scrapes all items from multiple wiki pages to build a complete database.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import urljoin, quote
import sys
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveItemScraper:
    def __init__(self):
        self.base_url = "https://stardewvalleywiki.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.items = {}
        self.next_id = 1
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a wiki page."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            time.sleep(0.5)  # Be respectful to the server
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_number(self, text: str) -> Optional[int]:
        """Extract number from text string."""
        if not text:
            return None
        # Remove commas and extract first number
        clean_text = str(text).replace(',', '').replace('g', '')
        match = re.search(r'(\d+)', clean_text)
        return int(match.group(1)) if match else None
    
    def clean_description(self, text: str) -> str:
        """Clean up description text."""
        if not text:
            return ""
        # Remove wiki markup and clean up
        text = re.sub(r'\[\[([^\]|]+)(\|[^\]]+)?\]\]', r'\1', text)  # Remove wiki links
        text = re.sub(r'\{\{[^}]+\}\}', '', text)  # Remove templates
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = text.replace('\n', ' ').strip()
        # Limit length
        if len(text) > 200:
            text = text[:197] + "..."
        return text
    
    def scrape_crops(self):
        """Scrape all crops from the crops page."""
        logger.info("Scraping crops...")
        soup = self.get_page(f"{self.base_url}/Crops")
        if not soup:
            return
            
        # Find crop tables
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                    
                try:
                    # Get crop name from first cell with link
                    name_cell = None
                    for cell in cells[:3]:
                        link = cell.find('a')
                        if link and link.get('title'):
                            name_cell = cell
                            break
                    
                    if not name_cell:
                        continue
                        
                    link = name_cell.find('a')
                    crop_name = link.get('title', '').strip()
                    if not crop_name or crop_name in self.items:
                        continue
                    
                    # Extract sell price from table
                    sell_price = None
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and any(c.isdigit() for c in cell_text):
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info from crop page
                    crop_url = urljoin(self.base_url, link.get('href', ''))
                    details = self.scrape_item_details(crop_url)
                    
                    self.items[crop_name] = {
                        'id': self.next_id,
                        'name': crop_name,
                        'description': details.get('description', f"A crop that can be grown and harvested."),
                        'category': 'Crops',
                        'sell_price': details.get('sell_price') or sell_price,
                        'energy': details.get('energy'),
                        'health': details.get('health')
                    }
                    
                    self.next_id += 1
                    logger.info(f"Added crop: {crop_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing crop row: {e}")
                    continue
    
    def scrape_fish(self):
        """Scrape all fish from the fish page."""
        logger.info("Scraping fish...")
        soup = self.get_page(f"{self.base_url}/Fish")
        if not soup:
            return
            
        # Find fish tables
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                try:
                    # Get fish name
                    name_cell = cells[0] if cells[0].find('a') else cells[1] if len(cells) > 1 else None
                    if not name_cell:
                        continue
                        
                    link = name_cell.find('a')
                    if not link:
                        continue
                        
                    fish_name = link.get('title', link.get_text()).strip()
                    if not fish_name or fish_name in self.items:
                        continue
                    
                    # Skip if it's not actually a fish (like "Fish" header)
                    if fish_name.lower() in ['fish', 'name', 'image']:
                        continue
                    
                    # Extract sell price
                    sell_price = None
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and any(c.isdigit() for c in cell_text):
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info
                    fish_url = urljoin(self.base_url, link.get('href', ''))
                    details = self.scrape_item_details(fish_url)
                    
                    self.items[fish_name] = {
                        'id': self.next_id,
                        'name': fish_name,
                        'description': details.get('description', f"A fish that can be caught."),
                        'category': 'Fish',
                        'sell_price': details.get('sell_price') or sell_price,
                        'energy': details.get('energy', 62),  # Default fish energy
                        'health': details.get('health', 27)   # Default fish health
                    }
                    
                    self.next_id += 1
                    logger.info(f"Added fish: {fish_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing fish row: {e}")
                    continue
    
    def scrape_foraging(self):
        """Scrape foraging items."""
        logger.info("Scraping foraging items...")
        soup = self.get_page(f"{self.base_url}/Foraging")
        if not soup:
            return
            
        # Find foraging tables
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                try:
                    # Get item name
                    name_cell = None
                    for cell in cells[:2]:
                        link = cell.find('a')
                        if link:
                            name_cell = cell
                            break
                    
                    if not name_cell:
                        continue
                        
                    link = name_cell.find('a')
                    item_name = link.get('title', link.get_text()).strip()
                    if not item_name or item_name in self.items:
                        continue
                    
                    # Extract sell price
                    sell_price = None
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and any(c.isdigit() for c in cell_text):
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info
                    item_url = urljoin(self.base_url, link.get('href', ''))
                    details = self.scrape_item_details(item_url)
                    
                    self.items[item_name] = {
                        'id': self.next_id,
                        'name': item_name,
                        'description': details.get('description', f"A foraged item found in nature."),
                        'category': 'Foraging',
                        'sell_price': details.get('sell_price') or sell_price,
                        'energy': details.get('energy', 62),
                        'health': details.get('health', 27)
                    }
                    
                    self.next_id += 1
                    logger.info(f"Added foraging item: {item_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing foraging row: {e}")
                    continue
    
    def scrape_minerals(self):
        """Scrape minerals and gems."""
        logger.info("Scraping minerals...")
        soup = self.get_page(f"{self.base_url}/Minerals")
        if not soup:
            return
            
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                try:
                    # Get mineral name
                    name_cell = cells[0] if cells[0].find('a') else cells[1] if len(cells) > 1 else None
                    if not name_cell:
                        continue
                        
                    link = name_cell.find('a')
                    if not link:
                        continue
                        
                    mineral_name = link.get('title', link.get_text()).strip()
                    if not mineral_name or mineral_name in self.items:
                        continue
                    
                    # Extract sell price
                    sell_price = None
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and any(c.isdigit() for c in cell_text):
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info
                    mineral_url = urljoin(self.base_url, link.get('href', ''))
                    details = self.scrape_item_details(mineral_url)
                    
                    self.items[mineral_name] = {
                        'id': self.next_id,
                        'name': mineral_name,
                        'description': details.get('description', f"A mineral found in the mines."),
                        'category': 'Minerals',
                        'sell_price': details.get('sell_price') or sell_price,
                        'energy': details.get('energy', -300),  # Most minerals are inedible
                        'health': details.get('health', -135)
                    }
                    
                    self.next_id += 1
                    logger.info(f"Added mineral: {mineral_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing mineral row: {e}")
                    continue
    
    def scrape_cooking(self):
        """Scrape cooking recipes and dishes."""
        logger.info("Scraping cooking items...")
        soup = self.get_page(f"{self.base_url}/Cooking")
        if not soup:
            return
            
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                try:
                    # Get dish name
                    name_cell = None
                    for cell in cells[:2]:
                        link = cell.find('a')
                        if link:
                            name_cell = cell
                            break
                    
                    if not name_cell:
                        continue
                        
                    link = name_cell.find('a')
                    dish_name = link.get('title', link.get_text()).strip()
                    if not dish_name or dish_name in self.items:
                        continue
                    
                    # Extract sell price
                    sell_price = None
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and any(c.isdigit() for c in cell_text):
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info
                    dish_url = urljoin(self.base_url, link.get('href', ''))
                    details = self.scrape_item_details(dish_url)
                    
                    self.items[dish_name] = {
                        'id': self.next_id,
                        'name': dish_name,
                        'description': details.get('description', f"A cooked dish."),
                        'category': 'Cooking',
                        'sell_price': details.get('sell_price') or sell_price,
                        'energy': details.get('energy', 100),  # Default cooking energy
                        'health': details.get('health', 45)
                    }
                    
                    self.next_id += 1
                    logger.info(f"Added cooking item: {dish_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing cooking row: {e}")
                    continue
    
    def scrape_artisan_goods(self):
        """Scrape artisan goods."""
        logger.info("Scraping artisan goods...")
        soup = self.get_page(f"{self.base_url}/Artisan_Goods")
        if not soup:
            return
            
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                    
                try:
                    # Get item name
                    name_cell = None
                    for cell in cells[:2]:
                        link = cell.find('a')
                        if link:
                            name_cell = cell
                            break
                    
                    if not name_cell:
                        continue
                        
                    link = name_cell.find('a')
                    item_name = link.get('title', link.get_text()).strip()
                    if not item_name or item_name in self.items:
                        continue
                    
                    # Extract sell price
                    sell_price = None
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and any(c.isdigit() for c in cell_text):
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info
                    item_url = urljoin(self.base_url, link.get('href', ''))
                    details = self.scrape_item_details(item_url)
                    
                    self.items[item_name] = {
                        'id': self.next_id,
                        'name': item_name,
                        'description': details.get('description', f"An artisan good."),
                        'category': 'Artisan Goods',
                        'sell_price': details.get('sell_price') or sell_price,
                        'energy': details.get('energy'),
                        'health': details.get('health')
                    }
                    
                    self.next_id += 1
                    logger.info(f"Added artisan good: {item_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing artisan good row: {e}")
                    continue
    
    def scrape_item_details(self, item_url: str) -> Dict:
        """Scrape detailed information from an item's individual page."""
        soup = self.get_page(item_url)
        if not soup:
            return {}
            
        try:
            details = {}
            
            # Look for infobox
            infobox = soup.find('table', class_='infobox')
            if infobox:
                rows = infobox.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        key = cells[0].get_text().strip().lower()
                        value = cells[1].get_text().strip()
                        
                        if 'sell price' in key or 'selling price' in key:
                            details['sell_price'] = self.extract_number(value)
                        elif 'energy' in key:
                            details['energy'] = self.extract_number(value)
                        elif 'health' in key:
                            details['health'] = self.extract_number(value)
            
            # Look for description in the first paragraph
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                first_p = content_div.find('p')
                if first_p:
                    description = first_p.get_text().strip()
                    description = self.clean_description(description)
                    if description and len(description) > 10:
                        details['description'] = description
            
            return details
            
        except Exception as e:
            logger.error(f"Error scraping item details from {item_url}: {e}")
            return {}
    
    def add_predefined_items(self):
        """Add important items that might be missed by scraping."""
        predefined = {
            # Common items that are essential for bundles
            "Wood": {"category": "Resources", "sell_price": 2, "description": "A basic building material."},
            "Stone": {"category": "Resources", "sell_price": 2, "description": "A common material used for crafting and building."},
            "Fiber": {"category": "Resources", "sell_price": 1, "description": "Raw material sourced from untamed plants."},
            "Sap": {"category": "Resources", "sell_price": 2, "description": "A fluid obtained from trees."},
            "Coal": {"category": "Resources", "sell_price": 15, "description": "A combustible rock that is useful for crafting and smelting."},
            "Copper Ore": {"category": "Resources", "sell_price": 5, "description": "A common ore that can be smelted into bars."},
            "Iron Ore": {"category": "Resources", "sell_price": 10, "description": "A fairly common ore that can be smelted into bars."},
            "Gold Ore": {"category": "Resources", "sell_price": 25, "description": "A precious ore that can be smelted into bars."},
            "Copper Bar": {"category": "Artisan Goods", "sell_price": 60, "description": "A bar of pure copper."},
            "Iron Bar": {"category": "Artisan Goods", "sell_price": 120, "description": "A bar of pure iron."},
            "Gold Bar": {"category": "Artisan Goods", "sell_price": 250, "description": "A bar of pure gold."},
            "Battery Pack": {"category": "Resources", "sell_price": 500, "description": "It's fully charged with energy."},
            "Hardwood": {"category": "Resources", "sell_price": 15, "description": "A special wood with superior strength and beauty."},
            "Slime": {"category": "Monster Loot", "sell_price": 5, "description": "A gooey substance with no particular use."},
            "Bat Wing": {"category": "Monster Loot", "sell_price": 15, "description": "The wing of a cave bat."},
            "Bug Meat": {"category": "Monster Loot", "sell_price": 8, "description": "A squishy, nutritious snack."},
        }
        
        for name, data in predefined.items():
            if name not in self.items:
                self.items[name] = {
                    'id': self.next_id,
                    'name': name,
                    'description': data['description'],
                    'category': data['category'],
                    'sell_price': data['sell_price'],
                    'energy': data.get('energy'),
                    'health': data.get('health')
                }
                self.next_id += 1
                logger.info(f"Added predefined item: {name}")
    
    def save_data(self):
        """Save scraped data to JSON files."""
        os.makedirs('data', exist_ok=True)
        
        # Convert items dict to list with proper IDs
        items_list = []
        for name, item_data in self.items.items():
            items_list.append(item_data)
        
        # Sort by ID
        items_list.sort(key=lambda x: x['id'])
        
        # Save items
        with open('data/items.json', 'w', encoding='utf-8') as f:
            json.dump(items_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(items_list)} items to data/items.json")
        
        # Also save a summary by category
        categories = {}
        for item in items_list:
            cat = item['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        logger.info("Items by category:")
        for cat, count in sorted(categories.items()):
            logger.info(f"  {cat}: {count}")
    
    def run(self):
        """Run the comprehensive scraping process."""
        logger.info("Starting comprehensive Stardew Valley item scraping...")
        
        # Scrape from different categories
        self.scrape_crops()
        self.scrape_fish()
        self.scrape_foraging()
        self.scrape_minerals()
        self.scrape_cooking()
        self.scrape_artisan_goods()
        
        # Add predefined items
        self.add_predefined_items()
        
        # Save everything
        self.save_data()
        
        logger.info(f"Comprehensive scraping completed! Total items: {len(self.items)}")

def main():
    scraper = ComprehensiveItemScraper()
    scraper.run()

if __name__ == "__main__":
    main()