// API configuration
const API_BASE_URL = 'http://localhost:8000';

// API endpoints
const API_ENDPOINTS = {
    tractors: '/marketplace/tractors',
    parts: '/marketplace/parts',
    featured: '/marketplace/featured',
    user: '/users/me',
    login: '/auth/login',
    register: '/auth/register',
};

// Generic fetch function with error handling
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// API functions
const api = {
    // Get all tractors
    async getTractors(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return fetchAPI(`${API_ENDPOINTS.tractors}?${queryString}`);
    },

    // Get a single tractor
    async getTractor(id) {
        return fetchAPI(`${API_ENDPOINTS.tractors}/${id}`);
    },

    // Get all parts
    async getParts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return fetchAPI(`${API_ENDPOINTS.parts}?${queryString}`);
    },

    // Get a single part
    async getPart(id) {
        return fetchAPI(`${API_ENDPOINTS.parts}/${id}`);
    },

    // Get featured listings
    async getFeatured() {
        return fetchAPI(API_ENDPOINTS.featured);
    },

    // User authentication
    async login(credentials) {
        return fetchAPI(API_ENDPOINTS.login, {
            method: 'POST',
            body: JSON.stringify(credentials),
        });
    },

    async register(userData) {
        return fetchAPI(API_ENDPOINTS.register, {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    },

    async getCurrentUser() {
        return fetchAPI(API_ENDPOINTS.user);
    },
};

// Export the API object
window.api = api; 