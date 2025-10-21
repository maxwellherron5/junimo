#!/usr/bin/env python3
"""
Stardew Valley Wiki Scraper
Scrapes item and bundle data from the Stardew Valley wiki to populate the database.
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

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StardewWikiScraper:
    def __init__(self):
        self.base_url = "https://stardewvalleywiki.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.items = {}
        self.bundles = []
        
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
        match = re.search(r'(\d+)', str(text).replace(',', ''))
        return int(match.group(1)) if match else None
    
    def scrape_items_from_category_page(self, category_url: str, category_name: str):
        """Scrape items from a category page."""
        soup = self.get_page(category_url)
        if not soup:
            return
            
        # Look for item tables
        tables = soup.find_all('table', class_='wikitable')
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                    
                try:
                    # Extract item name and link
                    name_cell = cells[0] if cells[0].get_text().strip() else cells[1]
                    name_link = name_cell.find('a')
                    
                    if not name_link:
                        continue
                        
                    item_name = name_link.get_text().strip()
                    item_url = urljoin(self.base_url, name_link.get('href', ''))
                    
                    # Skip if we already have this item
                    if item_name in self.items:
                        continue
                    
                    # Get basic info from table
                    sell_price = None
                    energy = None
                    health = None
                    
                    # Try to extract sell price from table
                    for cell in cells:
                        cell_text = cell.get_text().strip()
                        if 'g' in cell_text and cell_text.replace('g', '').replace(',', '').isdigit():
                            sell_price = self.extract_number(cell_text)
                            break
                    
                    # Get detailed info from item page
                    item_details = self.scrape_item_details(item_url)
                    
                    if item_details:
                        self.items[item_name] = {
                            'name': item_name,
                            'description': item_details.get('description', ''),
                            'category': category_name,
                            'sell_price': item_details.get('sell_price') or sell_price,
                            'energy': item_details.get('energy') or energy,
                            'health': item_details.get('health') or health,
                            'id': item_details.get('id') or len(self.items) + 1
                        }
                        
                        logger.info(f"Added item: {item_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing item row: {e}")
                    continue
    
    def scrape_item_details(self, item_url: str) -> Optional[Dict]:
        """Scrape detailed information from an item's individual page."""
        soup = self.get_page(item_url)
        if not soup:
            return None
            
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
                        elif 'id' in key:
                            details['id'] = self.extract_number(value)
            
            # Look for description in the first paragraph
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                first_p = content_div.find('p')
                if first_p:
                    description = first_p.get_text().strip()
                    # Clean up description
                    description = re.sub(r'\[.*?\]', '', description)  # Remove wiki links
                    description = description.replace('\n', ' ').strip()
                    if description and len(description) > 10:
                        details['description'] = description[:200] + '...' if len(description) > 200 else description
            
            return details
            
        except Exception as e:
            logger.error(f"Error scraping item details from {item_url}: {e}")
            return None
    
    def scrape_bundles(self):
        """Scrape community center bundles."""
        bundles_url = f"{self.base_url}/Bundles"
        soup = self.get_page(bundles_url)
        
        if not soup:
            logger.error("Could not fetch bundles page")
            return
        
        # Look for bundle tables
        bundle_sections = soup.find_all('table', class_='wikitable')
        
        bundle_id = 1
        
        for table in bundle_sections:
            # Try to find the room name from preceding headers
            room_name = "Unknown Room"
            prev_element = table.find_previous(['h2', 'h3', 'h4'])
            if prev_element:
                room_text = prev_element.get_text().strip()
                if 'room' in room_text.lower():
                    room_name = room_text.replace('[edit]', '').strip()
            
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:
                    continue
                
                try:
                    # Extract bundle name
                    bundle_name = cells[0].get_text().strip()
                    if not bundle_name or bundle_name == 'Bundle':
                        continue
                    
                    # Extract reward
                    reward = cells[-1].get_text().strip() if len(cells) > 2 else "Unknown reward"
                    
                    # Extract required items (usually in middle columns)
                    items_text = ""
                    for i in range(1, len(cells) - 1):
                        items_text += cells[i].get_text().strip() + " "
                    
                    # Parse items from text
                    bundle_items = self.parse_bundle_items(items_text)
                    
                    if bundle_items:
                        bundle = {
                            'id': bundle_id,
                            'name': bundle_name,
                            'room': room_name,
                            'reward': reward,
                            'items': bundle_items
                        }
                        
                        self.bundles.append(bundle)
                        logger.info(f"Added bundle: {bundle_name}")
                        bundle_id += 1
                        
                except Exception as e:
                    logger.error(f"Error processing bundle row: {e}")
                    continue
    
    def parse_bundle_items(self, items_text: str) -> List[Dict]:
        """Parse bundle items from text description."""
        items = []
        
        # Split by common separators
        item_parts = re.split(r'[,\n]', items_text)
        
        for part in item_parts:
            part = part.strip()
            if not part:
                continue
            
            # Extract quantity and item name
            quantity_match = re.search(r'(\d+)\s*(.+)', part)
            if quantity_match:
                quantity = int(quantity_match.group(1))
                item_name = quantity_match.group(2).strip()
            else:
                quantity = 1
                item_name = part
            
            # Clean item name
            item_name = re.sub(r'\(.*?\)', '', item_name).strip()
            item_name = item_name.replace('*', '').strip()
            
            # Find matching item ID
            item_id = None
            for stored_name, item_data in self.items.items():
                if stored_name.lower() == item_name.lower():
                    item_id = item_data['id']
                    break
            
            if item_id:
                items.append({
                    'item_id': item_id,
                    'quantity': quantity
                })
        
        return items
    
    def scrape_all_items(self):
        """Scrape items from various category pages."""
        categories = [
            ('Crops', f"{self.base_url}/Crops"),
            ('Foraging', f"{self.base_url}/Foraging"),
            ('Fishing', f"{self.base_url}/Fish"),
            ('Mining', f"{self.base_url}/Minerals"),
            ('Cooking', f"{self.base_url}/Cooking"),
            ('Artisan Goods', f"{self.base_url}/Artisan_Goods"),
            ('Animal Products', f"{self.base_url}/Animal_Products"),
        ]
        
        for category_name, category_url in categories:
            logger.info(f"Scraping category: {category_name}")
            self.scrape_items_from_category_page(category_url, category_name)
            time.sleep(1)  # Be respectful
    
    def save_data(self):
        """Save scraped data to JSON files."""
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Convert items dict to list with proper IDs
        items_list = []
        for i, (name, item_data) in enumerate(self.items.items(), 1):
            item_data['id'] = i
            items_list.append(item_data)
        
        # Update bundle item IDs to match the new item IDs
        for bundle in self.bundles:
            for bundle_item in bundle['items']:
                # Find the item by name and update ID
                for item in items_list:
                    if item['name'].lower() in [stored_name.lower() for stored_name in self.items.keys()]:
                        bundle_item['item_id'] = item['id']
                        break
        
        # Save items
        with open('data/items.json', 'w', encoding='utf-8') as f:
            json.dump(items_list, f, indent=2, ensure_ascii=False)
        
        # Save bundles
        with open('data/bundles.json', 'w', encoding='utf-8') as f:
            json.dump(self.bundles, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(items_list)} items and {len(self.bundles)} bundles")
    
    def run(self):
        """Run the complete scraping process."""
        logger.info("Starting Stardew Valley wiki scraping...")
        
        # Scrape items first
        self.scrape_all_items()
        
        # Then scrape bundles
        self.scrape_bundles()
        
        # Save everything
        self.save_data()
        
        logger.info("Scraping completed!")

def main():
    scraper = StardewWikiScraper()
    scraper.run()

if __name__ == "__main__":
    main()