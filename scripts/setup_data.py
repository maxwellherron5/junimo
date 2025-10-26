#!/usr/bin/env python3
"""
Junimo Data Setup Script
Comprehensive script to set up all game data for the Junimo Stardew Valley companion app.

This script:
1. Loads and validates items data with proper energy/health and seasonal information
2. Loads and validates bundles data
3. Loads and validates villagers data with gift preferences
4. Sets up the database with all necessary tables and data
5. Provides verification and statistics

Usage:
    python scripts/setup_data.py
"""

import json
import sqlite3
import os
from pathlib import Path

class JunimoDataSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.db_path = self.project_root / 'web-server' / 'junimo.db'
        self.data_dir = self.project_root / 'data'
        self.migrations_dir = self.project_root / 'migrations'
        
    def load_json_data(self, filename):
        """Load JSON data from the data directory"""
        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {filename} not found in {self.data_dir}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in {filename}: {e}")
            return []
    
    def run_migrations(self, conn):
        """Run all SQL migrations"""
        print("🔄 Running database migrations...")
        
        migration_files = sorted(self.migrations_dir.glob('*.sql'))
        
        for migration_file in migration_files:
            print(f"   Running {migration_file.name}...")
            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                    # Replace CREATE TABLE with CREATE TABLE IF NOT EXISTS
                    migration_sql = migration_sql.replace('CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ')
                    conn.executescript(migration_sql)
                print(f"   ✅ {migration_file.name} completed")
            except Exception as e:
                print(f"   ⚠️  Warning in {migration_file.name}: {e}")
                # Continue with other migrations
    
    def setup_items(self, conn):
        """Set up items data"""
        print("🔄 Setting up items data...")
        
        items = self.load_json_data('items.json')
        if not items:
            print("❌ No items data found")
            return 0
        
        cursor = conn.cursor()
        
        # Clear existing items
        cursor.execute('DELETE FROM items')
        
        # Insert items
        for item in items:
            cursor.execute('''
                INSERT INTO items (id, name, description, category, sell_price, energy, health, seasons, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['id'],
                item['name'],
                item.get('description'),
                item['category'],
                item.get('sell_price'),
                item.get('energy'),
                item.get('health'),
                json.dumps(item.get('seasons', [])) if item.get('seasons') else None,
                item.get('location')
            ))
        
        conn.commit()
        print(f"✅ Inserted {len(items)} items")
        return len(items)
    
    def setup_bundles(self, conn):
        """Set up bundles data"""
        print("🔄 Setting up bundles data...")
        
        bundles_data = self.load_json_data('bundles.json')
        if not bundles_data:
            print("❌ No bundles data found")
            return 0, 0
        
        cursor = conn.cursor()
        
        # Clear existing bundles
        cursor.execute('DELETE FROM bundle_items')
        cursor.execute('DELETE FROM bundles')
        
        bundle_count = 0
        item_count = 0
        
        # Insert bundles and their items
        for bundle in bundles_data:
            # Insert bundle
            cursor.execute('''
                INSERT INTO bundles (id, name, room, reward)
                VALUES (?, ?, ?, ?)
            ''', (
                bundle['id'],
                bundle['name'],
                bundle['room'],
                bundle['reward']
            ))
            bundle_count += 1
            
            # Insert bundle items
            for item in bundle.get('items', []):
                cursor.execute('''
                    INSERT INTO bundle_items (bundle_id, item_id, quantity)
                    VALUES (?, ?, ?)
                ''', (
                    bundle['id'],
                    item['item_id'],
                    item['quantity']
                ))
                item_count += 1
        
        conn.commit()
        print(f"✅ Inserted {bundle_count} bundles with {item_count} items")
        return bundle_count, item_count
    
    def setup_villagers(self, conn):
        """Set up villagers data"""
        print("🔄 Setting up villagers data...")
        
        villagers = self.load_json_data('villagers.json')
        if not villagers:
            print("❌ No villagers data found")
            return 0, 0
        
        cursor = conn.cursor()
        
        # Clear existing villagers
        cursor.execute('DELETE FROM villager_gift_preferences')
        cursor.execute('DELETE FROM villagers')
        
        villager_count = 0
        gift_count = 0
        
        # Insert villagers and their gift preferences
        for villager in villagers:
            # Insert villager
            cursor.execute('''
                INSERT INTO villagers (id, name, birthday, location, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                villager['id'],
                villager['name'],
                villager.get('birthday'),
                villager.get('location'),
                villager.get('description')
            ))
            villager_count += 1
            
            # Insert gift preferences
            for preference_type in ['loved_items', 'liked_items', 'neutral_items', 'disliked_items', 'hated_items']:
                items = villager.get(preference_type, [])
                pref_type = preference_type.replace('_items', '')
                
                for item_name in items:
                    cursor.execute('''
                        INSERT INTO villager_gift_preferences (villager_id, item_name, preference_type)
                        VALUES (?, ?, ?)
                    ''', (villager['id'], item_name, pref_type))
                    gift_count += 1
        
        conn.commit()
        print(f"✅ Inserted {villager_count} villagers with {gift_count} gift preferences")
        return villager_count, gift_count
    
    def verify_data(self, conn):
        """Verify the data integrity"""
        print("🔍 Verifying data integrity...")
        
        cursor = conn.cursor()
        
        # Check items
        cursor.execute('SELECT COUNT(*) FROM items')
        item_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM items WHERE energy IS NOT NULL AND energy > 0')
        consumable_items = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM items WHERE seasons IS NOT NULL')
        seasonal_items = cursor.fetchone()[0]
        
        # Check bundles
        cursor.execute('SELECT COUNT(*) FROM bundles')
        bundle_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM bundle_items')
        bundle_item_count = cursor.fetchone()[0]
        
        # Check villagers
        cursor.execute('SELECT COUNT(*) FROM villagers')
        villager_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM villager_gift_preferences')
        gift_pref_count = cursor.fetchone()[0]
        
        print(f"📊 Data Summary:")
        print(f"   Items: {item_count} total")
        print(f"   - Consumable items (with energy): {consumable_items}")
        print(f"   - Seasonal items: {seasonal_items}")
        print(f"   Bundles: {bundle_count} total")
        print(f"   - Bundle items: {bundle_item_count}")
        print(f"   Villagers: {villager_count} total")
        print(f"   - Gift preferences: {gift_pref_count}")
        
        # Check for data issues
        issues = []
        
        # Check for items with negative energy (should only be poisonous items)
        cursor.execute('SELECT name, energy FROM items WHERE energy < 0')
        negative_energy = cursor.fetchall()
        if negative_energy:
            print(f"   ⚠️  Items with negative energy: {len(negative_energy)}")
            for name, energy in negative_energy:
                print(f"      - {name}: {energy}")
        
        # Check for bundles without items
        cursor.execute('''
            SELECT b.name FROM bundles b 
            LEFT JOIN bundle_items bi ON b.id = bi.bundle_id 
            WHERE bi.bundle_id IS NULL
        ''')
        empty_bundles = cursor.fetchall()
        if empty_bundles:
            issues.append(f"Bundles without items: {[b[0] for b in empty_bundles]}")
        
        # Check for villagers without gift preferences
        cursor.execute('''
            SELECT v.name FROM villagers v 
            LEFT JOIN villager_gift_preferences vgp ON v.id = vgp.villager_id 
            WHERE vgp.villager_id IS NULL
        ''')
        villagers_no_gifts = cursor.fetchall()
        if villagers_no_gifts:
            issues.append(f"Villagers without gift preferences: {[v[0] for v in villagers_no_gifts]}")
        
        if issues:
            print("⚠️  Data Issues Found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ All data integrity checks passed!")
        
        return len(issues) == 0
    
    def setup_database(self):
        """Main setup function"""
        print("🍄 Setting up Junimo database...")
        print(f"Database path: {self.db_path}")
        
        # Ensure web-server directory exists
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Run migrations
            self.run_migrations(conn)
            
            # Setup data
            item_count = self.setup_items(conn)
            bundle_count, bundle_item_count = self.setup_bundles(conn)
            villager_count, gift_count = self.setup_villagers(conn)
            
            # Verify data
            data_valid = self.verify_data(conn)
            
            print("\n🎉 Database setup complete!")
            print(f"   📁 Database: {self.db_path}")
            print(f"   📊 Total records: {item_count + bundle_count + bundle_item_count + villager_count + gift_count}")
            
            if data_valid:
                print("✅ All data is valid and ready to use!")
            else:
                print("⚠️  Some data issues were found (see above)")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            return False
        finally:
            conn.close()

def main():
    """Main function"""
    setup = JunimoDataSetup()
    success = setup.setup_database()
    
    if success:
        print("\n🚀 Ready to run: cargo run (in web-server directory)")
        exit(0)
    else:
        print("\n💥 Setup failed!")
        exit(1)

if __name__ == "__main__":
    main()