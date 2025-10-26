class StardewCompanion {
    constructor() {
        this.items = [];
        this.bundles = [];
        this.villagers = [];
        this.progress = [];
        this.currentView = 'items';
        
        // Load progress from localStorage
        this.loadProgressFromStorage();
        
        this.init();
    }

    loadProgressFromStorage() {
        try {
            const stored = localStorage.getItem('junimo-progress');
            this.progress = stored ? JSON.parse(stored) : [];
            console.log('Loaded progress from localStorage:', this.progress.length, 'items');
        } catch (error) {
            console.error('Failed to load progress from localStorage:', error);
            this.progress = [];
        }
    }

    saveProgressToStorage() {
        try {
            localStorage.setItem('junimo-progress', JSON.stringify(this.progress));
            console.log('Saved progress to localStorage:', this.progress.length, 'items');
        } catch (error) {
            console.error('Failed to save progress to localStorage:', error);
        }
    }

    async init() {
        this.setupEventListeners();
        await this.waitForTauri();
        await this.loadData();
        this.renderCurrentView();
    }

    async waitForTauri() {
        // Wait for Tauri API to be available
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds max
        
        while (attempts < maxAttempts) {
            if (window.tauriAPI && window.tauriAPI.isAvailable) {
                console.log('API is ready!');
                return;
            }
            
            if (attempts % 10 === 0) {
                console.log(`Waiting for API... attempt ${attempts + 1}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        // If API is still not available, show error in UI
        const container = document.getElementById('items-grid');
        if (container) {
            container.innerHTML = `
                <div class="error-message" style="padding: 20px; color: red; text-align: center;">
                    <h3>API Not Available</h3>
                    <p>Unable to load the application API.</p>
                    <p>For Tauri: Make sure you're running <code>cargo tauri dev</code></p>
                    <p>For Browser: Use <code>browser-demo.html</code> instead</p>
                </div>
            `;
        }
        
        throw new Error('API failed to load after 5 seconds');
    }

    setupEventListeners() {
        // Navigation
        document.getElementById('items-tab').addEventListener('click', () => this.switchView('items'));
        document.getElementById('bundles-tab').addEventListener('click', () => this.switchView('bundles'));
        document.getElementById('villagers-tab').addEventListener('click', () => this.switchView('villagers'));
        document.getElementById('progress-tab').addEventListener('click', () => this.switchView('progress'));

        // Search
        document.getElementById('item-search').addEventListener('input', (e) => {
            this.searchItems(e.target.value);
        });

        // Season filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Update active button
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                // Filter items
                this.filterBySeason(e.target.dataset.season);
            });
        });
    }

    async loadData() {
        try {
            console.log('Loading data from backend...');
            console.log('API available:', window.tauriAPI?.isAvailable);
            
            if (!window.tauriAPI || !window.tauriAPI.isAvailable) {
                throw new Error('API is not available. Make sure the server is running.');
            }
            
            console.log('Calling get_items...');
            this.items = await window.tauriAPI.getItems();
            console.log('Received items:', this.items.length);
            
            console.log('Calling get_bundles...');
            this.bundles = await window.tauriAPI.getBundles();
            console.log('Received bundles:', this.bundles.length);
            
            console.log('Calling get_villagers...');
            this.villagers = await window.tauriAPI.getVillagers();
            console.log('Received villagers:', this.villagers.length);
            
            // Progress is now loaded from localStorage in constructor
            console.log('Using progress from localStorage:', this.progress.length);
            
            console.log('Data loading completed successfully');
        } catch (error) {
            console.error('Failed to load data:', error);
            console.error('Error details:', error.message, error.stack);
            this.showError(`Failed to load data: ${error.message}`);
        }
    }

    switchView(viewName) {
        console.log('switchView called with:', viewName);
        
        // Update navigation
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        const targetTab = document.getElementById(`${viewName}-tab`);
        if (targetTab) {
            targetTab.classList.add('active');
            console.log('Activated tab:', viewName);
        } else {
            console.error('Tab not found:', `${viewName}-tab`);
        }

        // Update views
        document.querySelectorAll('.tab-content').forEach(view => view.classList.remove('active'));
        const targetContent = document.getElementById(`${viewName}-content`);
        if (targetContent) {
            targetContent.classList.add('active');
            console.log('Activated content:', viewName);
        } else {
            console.error('Content not found:', `${viewName}-content`);
        }

        this.currentView = viewName;
        console.log('Current view set to:', this.currentView);
        this.renderCurrentView();
    }

    renderCurrentView() {
        console.log('renderCurrentView called for:', this.currentView);
        switch (this.currentView) {
            case 'items':
                console.log('Rendering items view');
                this.renderItems();
                break;
            case 'bundles':
                console.log('Rendering bundles view');
                this.renderBundles();
                break;
            case 'villagers':
                console.log('Rendering villagers view');
                this.renderVillagers();
                break;
            case 'progress':
                console.log('Rendering progress view');
                this.renderProgress();
                break;
            default:
                console.log('Unknown view:', this.currentView);
        }
    }

    renderItems(itemsToRender = this.items) {
        const container = document.getElementById('items-grid');
        
        console.log('Rendering items:', itemsToRender.length);
        console.log('Sample items:', itemsToRender.slice(0, 3));
        
        if (itemsToRender.length === 0) {
            console.log('No items to render, showing "No items found"');
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
        try {
            console.log('renderBundles called');
            console.log('Bundles count:', this.bundles.length);
            console.log('Sample bundles:', this.bundles.slice(0, 2));
            
            const container = document.getElementById('bundles-container');
            
            if (this.bundles.length === 0) {
                console.log('No bundles to render, showing "No bundles found"');
                container.innerHTML = '<div class="loading">No bundles found</div>';
                return;
            }

            console.log('Starting to render bundle cards...');
            const bundleCards = await Promise.all(this.bundles.map(async bundle => {
                try {
                    console.log('Processing bundle:', bundle.name, 'with id:', bundle.id);
                    const bundleItems = await window.tauriAPI.getBundleItems(bundle.id);
                    console.log('Got bundle items for', bundle.name, ':', bundleItems.length);
                    
                    if (!bundleItems || bundleItems.length === 0) {
                        console.log('No items found for bundle:', bundle.name);
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
                        try {
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
                        } catch (itemError) {
                            console.error('Error processing bundle item:', bundleItem, itemError);
                            return `<li class="bundle-item">Error loading item</li>`;
                        }
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
                } catch (bundleError) {
                    console.error('Error processing bundle:', bundle, bundleError);
                    return `
                        <div class="bundle-card">
                            <div class="bundle-header">
                                <div class="bundle-name">${bundle.name || 'Unknown Bundle'}</div>
                            </div>
                            <div class="error">Error loading bundle: ${bundleError.message}</div>
                        </div>
                    `;
                }
        }));

            console.log('Finished processing all bundles, setting innerHTML...');
            const finalHtml = bundleCards.join('');
            console.log('Final HTML length:', finalHtml.length);
            console.log('Sample HTML:', finalHtml.substring(0, 500));
            container.innerHTML = finalHtml;
            console.log('Bundle rendering complete');
        } catch (error) {
            console.error('Error in renderBundles:', error);
            const container = document.getElementById('bundles-container');
            container.innerHTML = '<div class="error">Error loading bundles: ' + error.message + '</div>';
        }
    }

    async renderProgress() {
        const container = document.getElementById('progress-container');
        
        try {
            // Calculate accurate totals by getting all bundle items
            let totalBundleItems = 0;
            const bundleProgress = [];
            
            for (const bundle of this.bundles) {
                const bundleItems = await window.tauriAPI.getBundleItems(bundle.id);
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
            const searchResults = await window.tauriAPI.searchItems(query);
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
            const seasons = this.parseSeasons(item.seasons);
            return seasons.includes(season);
        });

        this.renderItems(filteredItems);
    }

    async renderVillagers() {
        const container = document.getElementById('villagers-container');
        
        try {
            console.log('renderVillagers called');
            console.log('Villagers count:', this.villagers.length);
            
            if (this.villagers.length === 0) {
                container.innerHTML = '<div class="loading">No villagers found</div>';
                return;
            }

            const villagerCards = await Promise.all(this.villagers.map(async villager => {
                try {
                    const gifts = await window.tauriAPI.getVillagerGifts(villager.id);
                    
                    // Group gifts by preference type
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
                } catch (error) {
                    console.error('Error processing villager:', villager, error);
                    return `
                        <div class="villager-card">
                            <div class="villager-header">
                                <div class="villager-name">${villager.name || 'Unknown Villager'}</div>
                            </div>
                            <div class="error">Error loading villager data</div>
                        </div>
                    `;
                }
            }));

            container.innerHTML = villagerCards.join('');
            console.log('Villagers rendering complete');
        } catch (error) {
            console.error('Error in renderVillagers:', error);
            container.innerHTML = '<div class="error">Error loading villagers: ' + error.message + '</div>';
        }
    }

    toggleBundleItem(bundleItemId, completed) {
        console.log('toggleBundleItem called:', { bundleItemId, completed });
        try {
            // Find existing progress entry
            const existingIndex = this.progress.findIndex(p => p.bundle_item_id === bundleItemId);
            
            if (completed) {
                console.log('Marking item completed:', bundleItemId);
                if (existingIndex >= 0) {
                    // Update existing entry
                    this.progress[existingIndex].completed = true;
                    this.progress[existingIndex].completed_at = new Date().toISOString();
                } else {
                    // Create new entry
                    this.progress.push({
                        id: Date.now(), // Use timestamp as unique ID
                        bundle_item_id: bundleItemId,
                        completed: true,
                        completed_at: new Date().toISOString()
                    });
                }
            } else {
                console.log('Marking item incomplete:', bundleItemId);
                if (existingIndex >= 0) {
                    // Update existing entry
                    this.progress[existingIndex].completed = false;
                    this.progress[existingIndex].completed_at = null;
                }
            }
            
            // Save to localStorage
            this.saveProgressToStorage();
            console.log('Progress updated and saved to localStorage');
            
            // Update the current view to reflect changes
            if (this.currentView === 'bundles') {
                console.log('Re-rendering bundles view');
                this.renderBundles();
            } else if (this.currentView === 'progress') {
                console.log('Re-rendering progress view');
                this.renderProgress();
            }
        } catch (error) {
            console.error('Failed to update progress:', error);
            console.error('Error details:', error.message, error.stack);
            this.showError('Failed to update progress: ' + error.message);
        }
    }

    parseSeasons(seasonsData) {
        if (!seasonsData) return [];
        if (Array.isArray(seasonsData)) return seasonsData;
        try {
            return JSON.parse(seasonsData);
        } catch (e) {
            console.warn('Failed to parse seasons:', seasonsData);
            return [];
        }
    }

    clearProgress() {
        if (confirm('Are you sure you want to clear all progress? This cannot be undone.')) {
            this.progress = [];
            this.saveProgressToStorage();
            console.log('Progress cleared');
            
            // Re-render current view
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

// Initialize the app when the page loads
let app;

function initializeApp() {
    console.log('Initializing Junimo app...');
    console.log('Document ready state:', document.readyState);
    console.log('Window object available:', !!window);
    console.log('Tauri available at init:', !!window.__TAURI__);
    
    try {
        app = new StardewCompanion();
        window.app = app; // Make app globally accessible
        console.log('App initialized successfully');
    } catch (error) {
        console.error('Failed to initialize app:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    // Document is already loaded
    initializeApp();
}