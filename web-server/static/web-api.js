/**
 * Simple Web API client for Junimo standalone server
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
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'API request failed');
            }

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

    async getVillagers() {
        return await this.request('/villagers');
    }

    async getVillagerGifts(villagerId) {
        return await this.request(`/villagers/${villagerId}/gifts`);
    }
}

// Create global API instance
window.tauriAPI = new WebAPI();
console.log('🌐 Web API initialized');