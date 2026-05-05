class StaticAPI {
    constructor() {
        this._items = null;
        this._bundlesRaw = null;
        this._villagersRaw = null;
        this._bundleItemsByBundle = null;
    }

    async _fetchJson(path) {
        const response = await fetch(path);
        if (!response.ok) {
            throw new Error(`Failed to load ${path}: ${response.status}`);
        }
        return response.json();
    }

    async _loadBundles() {
        if (this._bundlesRaw) return this._bundlesRaw;
        this._bundlesRaw = await this._fetchJson('data/bundles.json');

        // Replicate the sequential bundle_item ids that the old SQL backend
        // assigned (bundle order in JSON, then item order within bundle).
        // localStorage progress keys off these ids — preserving the order
        // keeps any saved progress valid across the static migration.
        let nextId = 1;
        this._bundleItemsByBundle = new Map();
        for (const bundle of this._bundlesRaw) {
            const items = (bundle.items || []).map(item => ({
                id: nextId++,
                bundle_id: bundle.id,
                item_id: item.item_id,
                quantity: item.quantity,
                quality: item.quality ?? null,
            }));
            this._bundleItemsByBundle.set(bundle.id, items);
        }
        return this._bundlesRaw;
    }

    async getItems() {
        if (!this._items) {
            this._items = await this._fetchJson('data/items.json');
        }
        return this._items;
    }

    async searchItems(query) {
        const items = await this.getItems();
        const q = query.toLowerCase();
        return items.filter(item =>
            item.name.toLowerCase().includes(q) ||
            (item.description && item.description.toLowerCase().includes(q))
        );
    }

    async getBundles() {
        const bundles = await this._loadBundles();
        return bundles.map(({ id, name, room, reward }) => ({ id, name, room, reward }));
    }

    async getBundleItems(bundleId) {
        await this._loadBundles();
        return this._bundleItemsByBundle.get(bundleId) || [];
    }

    async getVillagers() {
        if (!this._villagersRaw) {
            this._villagersRaw = await this._fetchJson('data/villagers.json');
        }
        return this._villagersRaw.map(({ id, name, birthday, location, description }) =>
            ({ id, name, birthday, location, description }));
    }

    async getVillagerGifts(villagerId) {
        if (!this._villagersRaw) {
            this._villagersRaw = await this._fetchJson('data/villagers.json');
        }
        const villager = this._villagersRaw.find(v => v.id === villagerId);
        if (!villager) return [];

        const out = [];
        let nextId = 1;
        for (const type of ['loved', 'liked', 'neutral', 'disliked', 'hated']) {
            for (const itemName of villager[`${type}_items`] || []) {
                out.push({
                    id: nextId++,
                    villager_id: villagerId,
                    item_name: itemName,
                    preference_type: type,
                });
            }
        }
        return out;
    }
}

window.api = new StaticAPI();
