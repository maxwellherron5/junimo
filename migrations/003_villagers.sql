-- Create villagers table
CREATE TABLE IF NOT EXISTS villagers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birthday TEXT,
    location TEXT,
    description TEXT
);

-- Create villager_gift_preferences table
CREATE TABLE IF NOT EXISTS villager_gift_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    villager_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    preference_type TEXT NOT NULL CHECK (preference_type IN ('loved', 'liked', 'neutral', 'disliked', 'hated')),
    FOREIGN KEY (villager_id) REFERENCES villagers (id),
    UNIQUE(villager_id, item_name)
);