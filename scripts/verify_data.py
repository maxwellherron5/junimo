#!/usr/bin/env python3
"""
Data Verification Script
Shows statistics about the current database content.
"""

import sqlite3
import sys

def verify_database(db_path="junimo.db"):
    """Verify and display database statistics."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🎮 Junimo Database Statistics")
        print("=" * 40)
        
        # Total items
        cursor.execute("SELECT COUNT(*) FROM items")
        total_items = cursor.fetchone()[0]
        print(f"📦 Total Items: {total_items}")
        
        # Items by category
        cursor.execute("SELECT category, COUNT(*) FROM items GROUP BY category ORDER BY COUNT(*) DESC")
        categories = cursor.fetchall()
        print("\n📊 Items by Category:")
        for category, count in categories:
            print(f"   {category}: {count}")
        
        # Total bundles
        cursor.execute("SELECT COUNT(*) FROM bundles")
        total_bundles = cursor.fetchone()[0]
        print(f"\n🎁 Total Bundles: {total_bundles}")
        
        # Bundles by room
        cursor.execute("SELECT room, COUNT(*) FROM bundles GROUP BY room ORDER BY COUNT(*) DESC")
        rooms = cursor.fetchall()
        print("\n🏠 Bundles by Room:")
        for room, count in rooms:
            print(f"   {room}: {count}")
        
        # Bundle items
        cursor.execute("SELECT COUNT(*) FROM bundle_items")
        total_bundle_items = cursor.fetchone()[0]
        print(f"\n🔗 Total Bundle Items: {total_bundle_items}")
        
        # Sample high-value items
        cursor.execute("SELECT name, sell_price FROM items WHERE sell_price > 500 ORDER BY sell_price DESC LIMIT 5")
        valuable_items = cursor.fetchall()
        if valuable_items:
            print("\n💰 Most Valuable Items:")
            for name, price in valuable_items:
                print(f"   {name}: {price}g")
        
        # Sample items from each category
        print("\n🌟 Sample Items:")
        for category, _ in categories[:3]:  # Show top 3 categories
            cursor.execute("SELECT name FROM items WHERE category = ? LIMIT 3", (category,))
            items = cursor.fetchall()
            item_names = [item[0] for item in items]
            print(f"   {category}: {', '.join(item_names)}")
        
        conn.close()
        print("\n✅ Database verification completed!")
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Verify Junimo database')
    parser.add_argument('--db', default='junimo.db', help='Database file path')
    args = parser.parse_args()
    
    verify_database(args.db)