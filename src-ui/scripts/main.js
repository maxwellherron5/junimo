class StardewCompanion {
    constructor() {
        this.items = [];
        this.bundles = [];
        this.progress = [];
        this.currentView = 'items';
        
        this.init();
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
        document.getElementById('progress-tab').addEventListener('click', () => this.switchView('progress'));

        // Search
        document.getElementById('item-search').addEventListener('input', (e) => {
            this.searchItems(e.target.value);
        });
    }

    async loadData() {
        try {
            console.log('Loading data from Tauri backend...');
            console.log('Tauri API available:', window.tauriAPI?.isAvailable);
            
            if (!window.tauriAPI || !window.tauriAPI.isAvailable) {
                throw new Error('Tauri API is not available. Make sure you are running in Tauri environment.');
            }
            
            console.log('Calling get_items...');
            this.items = await window.tauriAPI.getItems();
            console.log('Received items:', this.items.length);
            
            console.log('Calling get_bundles...');
            this.bundles = await window.tauriAPI.getBundles();
            console.log('Received bundles:', this.bundles.length);
            
            console.log('Calling get_progress...');
            this.progress = await window.tauriAPI.getProgress();
            console.log('Received progress:', this.progress.length);
            
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
                <div class="item-stats">
                    ${item.sell_price ? `<span>Sell: ${item.sell_price}g</span>` : ''}
                    ${item.energy ? `<span>Energy: ${item.energy}</span>` : ''}
                    ${item.health ? `<span>Health: ${item.health}</span>` : ''}
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

    async toggleBundleItem(bundleItemId, completed) {
        console.log('toggleBundleItem called:', { bundleItemId, completed });
        try {
            if (completed) {
                console.log('Marking item completed:', bundleItemId);
                await window.tauriAPI.markItemCompleted(bundleItemId);
                console.log('Item marked completed successfully');
            } else {
                console.log('Marking item incomplete:', bundleItemId);
                await window.tauriAPI.markItemIncomplete(bundleItemId);
                console.log('Item marked incomplete successfully');
            }
            
            // Reload progress data
            console.log('Reloading progress data...');
            this.progress = await window.tauriAPI.getProgress();
            console.log('Progress reloaded:', this.progress.length, 'items');
            
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