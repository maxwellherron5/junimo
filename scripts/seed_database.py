#!/usr/bin/env python3
"""
Database Seeder for Stardew Valley Data
Populates the SQLite database with items and bundles data.
"""

import sqlite3
import json
import os
import sys
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseSeeder:
    def __init__(self, db_path: str = "junimo.db"):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            sys.exit(1)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def clear_existing_data(self):
        """Clear existing data from tables."""
        try:
            cursor = self.conn.cursor()
            
            # Clear in reverse order due to foreign key constraints
            cursor.execute("DELETE FROM user_progress")
            cursor.execute("DELETE FROM bundle_items")
            cursor.execute("DELETE FROM bundles")
            cursor.execute("DELETE FROM items")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('bundle_items', 'user_progress')")
            
            self.conn.commit()
            logger.info("Cleared existing data from database")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
            self.conn.rollback()
            raise
    
    def load_json_data(self) -> tuple[List[Dict], List[Dict]]:
        """Load items and bundles data from JSON files."""
        try:
            # Load items
            with open('data/items.json', 'r', encoding='utf-8') as f:
                items = json.load(f)
            
            # Load bundles
            with open('data/bundles.json', 'r', encoding='utf-8') as f:
                bundles = json.load(f)
            
            logger.info(f"Loaded {len(items)} items and {len(bundles)} bundles from JSON files")
            return items, bundles
            
        except FileNotFoundError as e:
            logger.error(f"JSON file not found: {e}")
            logger.error("Please run the scraper first to generate the data files")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading JSON data: {e}")
            sys.exit(1)
    
    def seed_items(self, items: List[Dict]):
        """Seed the items table."""
        try:
            cursor = self.conn.cursor()
            
            for item in items:
                cursor.execute("""
                    INSERT OR REPLACE INTO items (id, name, description, category, sell_price, energy, health)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item['id'],
                    item['name'],
                    item.get('description', ''),
                    item['category'],
                    item.get('sell_price'),
                    item.get('energy'),
                    item.get('health')
                ))
            
            self.conn.commit()
            logger.info(f"Seeded {len(items)} items")
            
        except Exception as e:
            logger.error(f"Error seeding items: {e}")
            self.conn.rollback()
            raise
    
    def seed_bundles(self, bundles: List[Dict]):
        """Seed the bundles and bundle_items tables."""
        try:
            cursor = self.conn.cursor()
            
            for bundle in bundles:
                # Insert bundle
                cursor.execute("""
                    INSERT OR REPLACE INTO bundles (id, name, room, reward)
                    VALUES (?, ?, ?, ?)
                """, (
                    bundle['id'],
                    bundle['name'],
                    bundle['room'],
                    bundle['reward']
                ))
                
                # Insert bundle items
                for bundle_item in bundle.get('items', []):
                    cursor.execute("""
                        INSERT INTO bundle_items (bundle_id, item_id, quantity, quality)
                        VALUES (?, ?, ?, ?)
                    """, (
                        bundle['id'],
                        bundle_item['item_id'],
                        bundle_item.get('quantity', 1),
                        bundle_item.get('quality')
                    ))
            
            self.conn.commit()
            logger.info(f"Seeded {len(bundles)} bundles")
            
        except Exception as e:
            logger.error(f"Error seeding bundles: {e}")
            self.conn.rollback()
            raise
    
    def verify_data(self):
        """Verify that data was inserted correctly."""
        try:
            cursor = self.conn.cursor()
            
            # Count items
            cursor.execute("SELECT COUNT(*) FROM items")
            item_count = cursor.fetchone()[0]
            
            # Count bundles
            cursor.execute("SELECT COUNT(*) FROM bundles")
            bundle_count = cursor.fetchone()[0]
            
            # Count bundle items
            cursor.execute("SELECT COUNT(*) FROM bundle_items")
            bundle_item_count = cursor.fetchone()[0]
            
            logger.info(f"Database verification:")
            logger.info(f"  Items: {item_count}")
            logger.info(f"  Bundles: {bundle_count}")
            logger.info(f"  Bundle Items: {bundle_item_count}")
            
            # Show some sample data
            cursor.execute("SELECT name, category FROM items LIMIT 5")
            sample_items = cursor.fetchall()
            logger.info("Sample items:")
            for item in sample_items:
                logger.info(f"  - {item['name']} ({item['category']})")
            
            cursor.execute("SELECT name, room FROM bundles LIMIT 5")
            sample_bundles = cursor.fetchall()
            logger.info("Sample bundles:")
            for bundle in sample_bundles:
                logger.info(f"  - {bundle['name']} ({bundle['room']})")
                
        except Exception as e:
            logger.error(f"Error verifying data: {e}")
    
    def run(self):
        """Run the complete seeding process."""
        logger.info("Starting database seeding...")
        
        # Check if database file exists
        if not os.path.exists(self.db_path):
            logger.error(f"Database file {self.db_path} not found!")
            logger.error("Please run migrations first: sqlx migrate run")
            sys.exit(1)
        
        try:
            self.connect()
            
            # Load data from JSON files
            items, bundles = self.load_json_data()
            
            # Clear existing data
            self.clear_existing_data()
            
            # Seed new data
            self.seed_items(items)
            self.seed_bundles(bundles)
            
            # Verify the data
            self.verify_data()
            
            logger.info("Database seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            sys.exit(1)
        finally:
            self.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed Stardew Valley database')
    parser.add_argument('--db', default='junimo.db', help='Database file path')
    parser.add_argument('--generate-data', action='store_true', 
                       help='Generate data files first using the scraper')
    
    args = parser.parse_args()
    
    # Generate data if requested
    if args.generate_data:
        logger.info("Generating data files first...")
        import subprocess
        try:
            subprocess.run([sys.executable, 'scripts/scrape_bundles_specific.py'], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate data: {e}")
            sys.exit(1)
    
    # Seed the database
    seeder = DatabaseSeeder(args.db)
    seeder.run()

if __name__ == "__main__":
    main()