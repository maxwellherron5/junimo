-- Items table
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    sell_price INTEGER,
    energy INTEGER,
    health INTEGER
);

-- Bundles table
CREATE TABLE bundles (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    room TEXT NOT NULL,
    reward TEXT NOT NULL
);

-- Bundle items table (many-to-many relationship between bundles and items)
CREATE TABLE bundle_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    quality TEXT,
    FOREIGN KEY (bundle_id) REFERENCES bundles (id),
    FOREIGN KEY (item_id) REFERENCES items (id)
);

-- User progress table
CREATE TABLE user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_item_id INTEGER NOT NULL UNIQUE,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at DATETIME,
    FOREIGN KEY (bundle_item_id) REFERENCES bundle_items (id)
);

-- Indexes for better performance
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_bundle_items_bundle_id ON bundle_items(bundle_id);
CREATE INDEX idx_bundle_items_item_id ON bundle_items(item_id);
CREATE INDEX idx_user_progress_bundle_item_id ON user_progress(bundle_item_id);