/**
 * Web API client for Junimo
 * Communicates with the Rust Poem web server
 */

class WebAPI {
    constructor() {
        this.isAvailable = true;
        this.baseUrl = '/api';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            console.log(`API Request: ${config.method || 'GET'} ${url}`);
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'API request failed');
            }

            console.log(`API Response: ${url} - ${data.data?.length || 'N/A'} items`);
            return data.data;
        } catch (error) {
            console.error(`API Error: ${url}`, error);
            throw error;
        }
    }

    async getItems() {
        return await this.request('/items');
    }

    async searchItems(query) {
        return await this.request(`/items/search?q=${encodeURIComponent(query)}`);
    }

    async getBundles() {
        return await this.request('/bundles');
    }

    async getBundleItems(bundleId) {
        return await this.request(`/bundles/${bundleId}/items`);
    }

    async markItemCompleted(bundleItemId) {
        return await this.request('/progress/complete', {
            method: 'POST',
            body: JSON.stringify({ bundleItemId }),
        });
    }

    async markItemIncomplete(bundleItemId) {
        return await this.request('/progress/incomplete', {
            method: 'POST',
            body: JSON.stringify({ bundleItemId }),
        });
    }

    async getProgress() {
        return await this.request('/progress');
    }
}

// Create global API instance
window.tauriAPI = new WebAPI();

console.log('🌐 Web API initialized');