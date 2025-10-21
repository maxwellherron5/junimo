#!/usr/bin/env python3
"""
Add missing items that are referenced in bundles.
"""

import sqlite3

def add_missing_items():
    """Add missing items to the database."""
    
    # Missing items with their details
    missing_items = [
        # Fish
        (136, "Largemouth Bass", "A popular fish that lives in lakes.", "Fish", 100, 62, 27),
        (142, "Carp", "A common pond fish.", "Fish", 30, 62, 27),
        (143, "Catfish", "An uncommon fish found in rivers.", "Fish", 200, 62, 27),
        (145, "Sunfish", "A common river fish.", "Fish", 30, 62, 27),
        (174, "Large White Egg", "A large white chicken egg.", "Animal Products", 95, 125, 56),
        (178, "Hay", "Dried grass used as animal feed.", "Animal Products", 0, -300, -135),
        (194, "Fried Egg", "Sunny-side up.", "Cooking", 35, 50, 22),
        (228, "Maki Roll", "Fish and rice wrapped in seaweed.", "Cooking", 220, 100, 45),
        (254, "Melon", "A sweet summer treat.", "Crops", 250, 113, 50),
        (256, "Tomato", "Rich and slightly tangy.", "Crops", 60, 25, 11),
        (258, "Blueberry", "A popular berry reported to have many health benefits.", "Crops", 50, 25, 11),
        (259, "Fiddlehead Fern", "The young shoots are considered a delicacy.", "Foraging", 90, 90, 40),
        (260, "Hot Pepper", "Fiery hot!", "Crops", 40, 25, 11),
        (262, "Wheat", "One of the most widely cultivated grains.", "Crops", 25, 25, 11),
        (270, "Corn", "One of the most popular grains.", "Crops", 50, 25, 11),
        (272, "Eggplant", "A rich and wholesome relative of the tomato.", "Crops", 60, 25, 11),
        (276, "Pumpkin", "A fall favorite.", "Crops", 320, 225, 101),
        (281, "Chanterelle", "A tasty mushroom with a fruity smell and slightly peppery flavor.", "Foraging", 160, 62, 27),
        (283, "Holly", "The leaves and bright red berries make a popular winter decoration.", "Foraging", 80, 62, 27),
        (284, "Beet", "A sweet and earthy root veggie.", "Crops", 100, 62, 27),
        
        # Bars and Resources
        (334, "Copper Bar", "A copper bar.", "Resources", 60, -300, -135),
        (335, "Iron Bar", "An iron bar.", "Resources", 120, -300, -135),
        (336, "Gold Bar", "A gold bar.", "Resources", 250, -300, -135),
        (340, "Honey", "It's a sweet syrup produced by bees.", "Artisan Goods", 100, 101, 45),
        (344, "Jelly", "It's made from fruit.", "Artisan Goods", 160, 101, 45),
        (348, "Wine", "Drink in moderation.", "Artisan Goods", 400, 101, 45),
        (372, "Clam", "Someone lived in this shell.", "Fish", 50, 62, 27),
        (376, "Poppy", "In addition to its colorful flower, the Poppy has culinary and medicinal uses.", "Foraging", 140, 25, 11),
        (388, "Wood", "A basic building material.", "Resources", 2, -300, -135),
        (390, "Stone", "A common material with many uses in crafting and building.", "Resources", 2, -300, -135),
        (392, "Nautilus Shell", "An ancient shell.", "Fish", 120, -300, -135),
        (397, "Sea Urchin", "A spiny creature that some consider a delicacy.", "Fish", 160, -300, -135),
        (420, "Red Mushroom", "A spotted mushroom sometimes found in caves.", "Foraging", 75, 62, 27),
        (422, "Purple Mushroom", "A rare mushroom found deep in caves.", "Foraging", 125, 62, 27),
        (424, "Cheese", "It's your basic cheese.", "Artisan Goods", 200, 125, 56),
        (426, "Goat Cheese", "Soft cheese made from goat's milk.", "Artisan Goods", 400, 125, 56),
        (430, "Truffle", "A gourmet type of mushroom with a unique taste.", "Animal Products", 625, 125, 56),
        (433, "Sunflower", "A common misconception is that the flower turns so it's always facing the sun.", "Crops", 90, 25, 11),
        (444, "Duck Feather", "It's so colorful.", "Animal Products", 125, -300, -135),
        (446, "Rabbit's Foot", "Some say it's lucky.", "Animal Products", 565, -300, -135),
        (459, "Mead", "A fermented beverage made from honey.", "Artisan Goods", 200, 101, 45),
        (613, "Apple", "A crisp fruit used for juice and cider.", "Crops", 100, 125, 56),
        
        # Combat Items
        (684, "Bug Meat", "It's a squishy, insect-like substance.", "Monster Loot", 8, 62, 27),
        (698, "Sturgeon", "An ancient bottom-feeder with a dwindling population.", "Fish", 200, 62, 27),
        (700, "Bullhead", "A relative of the catfish that eats a variety of foods off the lake bottom.", "Fish", 75, 62, 27),
        (701, "Tilapia", "A primarily vegetarian fish that prefers warm water.", "Fish", 75, 62, 27),
        (702, "Chub", "A common freshwater fish known for its voracious appetite.", "Fish", 50, 62, 27),
        (706, "Shad", "Lives in a school in lakes.", "Fish", 60, 62, 27),
        (709, "Hardwood", "A special wood with superior strength and beauty.", "Resources", 15, -300, -135),
        (724, "Maple Syrup", "A sweet syrup with a unique flavor.", "Artisan Goods", 200, 125, 56),
        (725, "Oak Resin", "A sticky, fragrant substance derived from oak trees.", "Artisan Goods", 150, -300, -135),
        (766, "Slime", "A gooey substance with no particular use.", "Monster Loot", 5, -300, -135),
        (767, "Bat Wing", "The wing of a cave-dwelling bat.", "Monster Loot", 15, -300, -135),
    ]
    
    conn = sqlite3.connect('junimo.db')
    cursor = conn.cursor()
    
    print(f"Adding {len(missing_items)} missing items...")
    
    for item_id, name, description, category, sell_price, energy, health in missing_items:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO items (id, name, description, category, sell_price, energy, health)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (item_id, name, description, category, sell_price, energy, health))
            print(f"Added: {name} (ID {item_id})")
        except Exception as e:
            print(f"Error adding {name}: {e}")
    
    conn.commit()
    
    # Verify the additions
    cursor.execute("SELECT COUNT(*) FROM items")
    total_items = cursor.fetchone()[0]
    print(f"\nTotal items in database: {total_items}")
    
    # Check how many bundle items now have matching items
    cursor.execute("""
        SELECT COUNT(*) FROM bundle_items bi 
        JOIN items i ON bi.item_id = i.id
    """)
    matched_items = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM bundle_items")
    total_bundle_items = cursor.fetchone()[0]
    
    print(f"Bundle items with matching items: {matched_items}/{total_bundle_items}")
    
    conn.close()

if __name__ == "__main__":
    add_missing_items()