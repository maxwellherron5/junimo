class StardewCompanion {
    constructor() {
        this.items = [];
        this.bundles = [];
        this.villagers = [];
        this.progress = [];
        this.currentView = 'items';

        this.loadProgressFromStorage();
        this.init();
    }

    loadProgressFromStorage() {
        try {
            const stored = localStorage.getItem('junimo-progress');
            this.progress = stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Failed to load progress from localStorage:', error);
            this.progress = [];
        }
    }

    saveProgressToStorage() {
        try {
            localStorage.setItem('junimo-progress', JSON.stringify(this.progress));
        } catch (error) {
            console.error('Failed to save progress to localStorage:', error);
        }
    }

    async init() {
        this.setupEventListeners();
        await this.loadData();
        this.renderCurrentView();
    }

    setupEventListeners() {
        document.getElementById('items-tab').addEventListener('click', () => this.switchView('items'));
        document.getElementById('bundles-tab').addEventListener('click', () => this.switchView('bundles'));
        document.getElementById('villagers-tab').addEventListener('click', () => this.switchView('villagers'));
        document.getElementById('progress-tab').addEventListener('click', () => this.switchView('progress'));

        document.getElementById('item-search').addEventListener('input', (e) => {
            this.searchItems(e.target.value);
        });

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.filterBySeason(e.target.dataset.season);
            });
        });
    }

    async loadData() {
        try {
            this.items = await window.api.getItems();
            this.bundles = await window.api.getBundles();
            this.villagers = await window.api.getVillagers();
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showError(`Failed to load data: ${error.message}`);
        }
    }

    switchView(viewName) {
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${viewName}-tab`)?.classList.add('active');

        document.querySelectorAll('.tab-content').forEach(view => view.classList.remove('active'));
        document.getElementById(`${viewName}-content`)?.classList.add('active');

        this.currentView = viewName;
        this.renderCurrentView();
    }

    renderCurrentView() {
        switch (this.currentView) {
            case 'items': this.renderItems(); break;
            case 'bundles': this.renderBundles(); break;
            case 'villagers': this.renderVillagers(); break;
            case 'progress': this.renderProgress(); break;
        }
    }

    renderItems(itemsToRender = this.items) {
        const container = document.getElementById('items-grid');

        if (itemsToRender.length === 0) {
            container.innerHTML = '<div class="loading">No items found</div>';
            return;
        }

        container.innerHTML = itemsToRender.map(item => `
            <div class="item-card">
                <div class="item-name">${item.name}</div>
                <div class="item-category">${item.category}</div>
                ${item.description ? `<div class="item-description">${item.description}</div>` : ''}
                ${item.seasons ? `<div class="item-seasons">🗓️ ${this.parseSeasons(item.seasons).join(', ')}</div>` : ''}
                ${item.location ? `<div class="item-location">📍 ${item.location}</div>` : ''}
                <div class="item-stats">
                    ${item.sell_price ? `<span>💰 ${item.sell_price}g</span>` : ''}
                    ${item.energy && item.energy > 0 ? `<span>⚡ ${item.energy}</span>` : ''}
                    ${item.health && item.health > 0 ? `<span>❤️ ${item.health}</span>` : ''}
                    ${item.energy && item.energy < 0 ? `<span style="color: #dc3545;">☠️ ${Math.abs(item.energy)}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    async renderBundles() {
        const container = document.getElementById('bundles-container');

        try {
            if (this.bundles.length === 0) {
                container.innerHTML = '<div class="loading">No bundles found</div>';
                return;
            }

            const bundleCards = await Promise.all(this.bundles.map(async bundle => {
                const bundleItems = await window.api.getBundleItems(bundle.id);

                if (!bundleItems || bundleItems.length === 0) {
                    return `
                        <div class="bundle-card">
                            <div class="bundle-header">
                                <div class="bundle-name">${bundle.name}</div>
                                <div class="bundle-room">${bundle.room}</div>
                                <div class="bundle-reward">Reward: ${bundle.reward}</div>
                            </div>
                            <div class="bundle-items">No items found for this bundle</div>
                        </div>
                    `;
                }

                const itemsHtml = bundleItems.map(bundleItem => {
                    const item = this.items.find(i => i.id === bundleItem.item_id);
                    const isCompleted = this.progress.some(p => p.bundle_item_id === bundleItem.id && p.completed);

                    return `
                        <li class="bundle-item ${isCompleted ? 'completed' : ''}">
                            <div class="bundle-item-info">
                                <div class="bundle-item-name">${item ? item.name : 'Unknown Item'}</div>
                                <div class="bundle-item-quantity">Quantity: ${bundleItem.quantity}</div>
                            </div>
                            <input
                                type="checkbox"
                                class="bundle-item-checkbox"
                                ${isCompleted ? 'checked' : ''}
                                onchange="app.toggleBundleItem(${bundleItem.id}, this.checked)"
                            >
                        </li>
                    `;
                }).join('');

                return `
                    <div class="bundle-card">
                        <div class="bundle-header">
                            <div class="bundle-name">${bundle.name}</div>
                            <div class="bundle-room">${bundle.room}</div>
                            <div class="bundle-reward">Reward: ${bundle.reward}</div>
                        </div>
                        <ul class="bundle-items">
                            ${itemsHtml}
                        </ul>
                    </div>
                `;
            }));

            container.innerHTML = bundleCards.join('');
        } catch (error) {
            console.error('Error rendering bundles:', error);
            container.innerHTML = `<div class="error">Error loading bundles: ${error.message}</div>`;
        }
    }

    async renderProgress() {
        const container = document.getElementById('progress-container');

        try {
            let totalBundleItems = 0;
            const bundleProgress = [];

            for (const bundle of this.bundles) {
                const bundleItems = await window.api.getBundleItems(bundle.id);
                const completedInBundle = bundleItems.filter(item =>
                    this.progress.some(p => p.bundle_item_id === item.id && p.completed)
                ).length;

                bundleProgress.push({
                    bundle,
                    total: bundleItems.length,
                    completed: completedInBundle,
                    percentage: bundleItems.length > 0 ? Math.round((completedInBundle / bundleItems.length) * 100) : 0
                });

                totalBundleItems += bundleItems.length;
            }

            const completedItems = this.progress.filter(p => p.completed).length;
            const overallPercentage = totalBundleItems > 0 ? Math.round((completedItems / totalBundleItems) * 100) : 0;

            const bundleProgressHtml = bundleProgress.map(bp => `
                <div class="bundle-progress-card">
                    <div class="bundle-progress-header">
                        <div class="bundle-progress-name">${bp.bundle.name}</div>
                        <div class="bundle-progress-room">${bp.bundle.room}</div>
                    </div>
                    <div class="bundle-progress-bar">
                        <div class="bundle-progress-fill" style="width: ${bp.percentage}%"></div>
                    </div>
                    <div class="bundle-progress-stats">
                        <span>${bp.completed}/${bp.total} items (${bp.percentage}%)</span>
                    </div>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="progress-summary">
                    <h2>Progress Summary</h2>
                    <div class="progress-stats">
                        <div class="progress-stat">
                            <div class="progress-stat-value">${completedItems}</div>
                            <div class="progress-stat-label">Items Completed</div>
                        </div>
                        <div class="progress-stat">
                            <div class="progress-stat-value">${totalBundleItems}</div>
                            <div class="progress-stat-label">Total Items</div>
                        </div>
                        <div class="progress-stat">
                            <div class="progress-stat-value">${overallPercentage}%</div>
                            <div class="progress-stat-label">Overall Progress</div>
                        </div>
                    </div>
                    <div class="overall-progress-bar">
                        <div class="overall-progress-fill" style="width: ${overallPercentage}%"></div>
                    </div>
                    <div style="margin-top: 1rem; text-align: center;">
                        <button onclick="app.clearProgress()" style="padding: 0.5rem 1rem; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            Clear All Progress
                        </button>
                        <p style="font-size: 0.8rem; color: #666; margin-top: 0.5rem;">
                            Progress is saved locally in your browser
                        </p>
                    </div>
                </div>

                <div class="bundle-progress-container">
                    <h3>Bundle Progress</h3>
                    ${bundleProgressHtml}
                </div>
            `;
        } catch (error) {
            console.error('Error rendering progress:', error);
            container.innerHTML = `
                <div class="error">
                    <h2>Error Loading Progress</h2>
                    <p>Failed to load progress data: ${error.message}</p>
                </div>
            `;
        }
    }

    async searchItems(query) {
        if (!query.trim()) {
            this.renderItems();
            return;
        }

        try {
            const searchResults = await window.api.searchItems(query);
            this.renderItems(searchResults);
        } catch (error) {
            console.error('Search failed:', error);
            this.showError('Search failed');
        }
    }

    filterBySeason(season) {
        if (season === 'all') {
            this.renderItems();
            return;
        }

        const filteredItems = this.items.filter(item => {
            if (!item.seasons) return false;
            return this.parseSeasons(item.seasons).includes(season);
        });

        this.renderItems(filteredItems);
    }

    async renderVillagers() {
        const container = document.getElementById('villagers-container');

        try {
            if (this.villagers.length === 0) {
                container.innerHTML = '<div class="loading">No villagers found</div>';
                return;
            }

            const villagerCards = await Promise.all(this.villagers.map(async villager => {
                const gifts = await window.api.getVillagerGifts(villager.id);

                const giftsByType = {
                    loved: gifts.filter(g => g.preference_type === 'loved'),
                    liked: gifts.filter(g => g.preference_type === 'liked'),
                    disliked: gifts.filter(g => g.preference_type === 'disliked'),
                    hated: gifts.filter(g => g.preference_type === 'hated')
                };

                const renderGiftCategory = (type, items, icon) => {
                    if (items.length === 0) return '';
                    return `
                        <div class="gift-category ${type}">
                            <div class="gift-category-title">
                                ${icon} ${type.charAt(0).toUpperCase() + type.slice(1)}
                            </div>
                            <div class="gift-items">
                                ${items.map(item => `<span class="gift-item">${item.item_name}</span>`).join('')}
                            </div>
                        </div>
                    `;
                };

                return `
                    <div class="villager-card">
                        <div class="villager-header">
                            <div class="villager-name">${villager.name}</div>
                            ${villager.birthday ? `<div class="villager-birthday">🎂 ${villager.birthday}</div>` : ''}
                            ${villager.location ? `<div class="villager-location">📍 ${villager.location}</div>` : ''}
                        </div>
                        ${villager.description ? `<div class="villager-description">${villager.description}</div>` : ''}
                        <div class="gift-preferences">
                            ${renderGiftCategory('loved', giftsByType.loved, '💖')}
                            ${renderGiftCategory('liked', giftsByType.liked, '👍')}
                            ${renderGiftCategory('disliked', giftsByType.disliked, '👎')}
                            ${renderGiftCategory('hated', giftsByType.hated, '💔')}
                        </div>
                    </div>
                `;
            }));

            container.innerHTML = villagerCards.join('');
        } catch (error) {
            console.error('Error rendering villagers:', error);
            container.innerHTML = `<div class="error">Error loading villagers: ${error.message}</div>`;
        }
    }

    toggleBundleItem(bundleItemId, completed) {
        const existingIndex = this.progress.findIndex(p => p.bundle_item_id === bundleItemId);

        if (completed) {
            if (existingIndex >= 0) {
                this.progress[existingIndex].completed = true;
                this.progress[existingIndex].completed_at = new Date().toISOString();
            } else {
                this.progress.push({
                    id: Date.now(),
                    bundle_item_id: bundleItemId,
                    completed: true,
                    completed_at: new Date().toISOString()
                });
            }
        } else if (existingIndex >= 0) {
            this.progress[existingIndex].completed = false;
            this.progress[existingIndex].completed_at = null;
        }

        this.saveProgressToStorage();

        if (this.currentView === 'bundles') {
            this.renderBundles();
        } else if (this.currentView === 'progress') {
            this.renderProgress();
        }
    }

    parseSeasons(seasonsData) {
        if (!seasonsData) return [];
        if (Array.isArray(seasonsData)) return seasonsData;
        try {
            return JSON.parse(seasonsData);
        } catch (e) {
            return [];
        }
    }

    clearProgress() {
        if (confirm('Are you sure you want to clear all progress? This cannot be undone.')) {
            this.progress = [];
            this.saveProgressToStorage();
            this.renderCurrentView();
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.style.cssText = 'padding: 10px; background: #ffebee; color: #c62828; border: 1px solid #ef5350; margin: 10px 0; border-radius: 4px;';
        errorDiv.textContent = message;

        const main = document.querySelector('main');
        main.insertBefore(errorDiv, main.firstChild);

        setTimeout(() => errorDiv.remove(), 5000);
    }
}

let app;

function initializeApp() {
    app = new StardewCompanion();
    window.app = app;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
