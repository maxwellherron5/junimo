CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    sell_price INTEGER,
    energy INTEGER,
    health INTEGER,
    seasons TEXT,
    location TEXT
);

CREATE TABLE bundles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    room TEXT NOT NULL,
    reward TEXT NOT NULL
);

CREATE TABLE bundle_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    quality TEXT,
    FOREIGN KEY (bundle_id) REFERENCES bundles (id),
    FOREIGN KEY (item_id) REFERENCES items (id)
);

CREATE TABLE villagers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    birthday TEXT,
    location TEXT,
    description TEXT
);

CREATE TABLE villager_gift_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    villager_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    preference_type TEXT NOT NULL CHECK (preference_type IN ('loved', 'liked', 'neutral', 'disliked', 'hated')),
    FOREIGN KEY (villager_id) REFERENCES villagers (id),
    UNIQUE(villager_id, item_name)
);

CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_bundle_items_bundle_id ON bundle_items(bundle_id);
CREATE INDEX idx_bundle_items_item_id ON bundle_items(item_id);
