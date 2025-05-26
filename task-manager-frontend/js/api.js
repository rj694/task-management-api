// API base URL - change this to your API endpoint
const API_BASE_URL = 'http://localhost:5000/api/v1';

// API service for making requests
const api = {
    // Set auth token
    setToken(token) {
        localStorage.setItem('accessToken', token);
    },

    // Get auth token
    getToken() {
        return localStorage.getItem('accessToken');
    },

    // Remove auth token
    removeToken() {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
    },

    // Save refresh token
    setRefreshToken(token) {
        localStorage.setItem('refreshToken', token);
    },

    // Get refresh token
    getRefreshToken() {
        return localStorage.getItem('refreshToken');
    },

    // Save user data
    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    // Get user data
    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Common fetch method with auth
    async fetch(endpoint, options = {}) {
        const token = this.getToken();
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            }
        };

        const fetchOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);
            
            // Handle rate limiting
            if (response.status === 429) {
                const retryAfter = response.headers.get('X-RateLimit-Reset') || '60';
                throw new Error(`Rate limit exceeded. Please wait ${retryAfter} seconds before trying again.`);
            }
            
            // Handle token expiration
            if (response.status === 401) {
                const responseBody = await response.json();
                // Only try refresh if it's an expired token
                if (responseBody.error === 'Token has expired') {
                    try {
                        const refreshed = await this.refreshToken();
                        if (refreshed) {
                            // Retry the original request with the new token
                            fetchOptions.headers['Authorization'] = `Bearer ${this.getToken()}`;
                            return fetch(`${API_BASE_URL}${endpoint}`, fetchOptions);
                        }
                    } catch (refreshError) {
                        // If refresh fails, logout and redirect to login
                        this.removeToken();
                        window.location.href = '/login.html';
                        throw new Error('Session expired. Please log in again.');
                    }
                }
            }
            
            // Regular response handling
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || errorData.message || 'Something went wrong');
            }
            
            // If the response is 204 No Content, return null
            if (response.status === 204) {
                return null;
            }
            
            return await response.json();
        } catch (error) {
            // Handle network errors
            if (error instanceof TypeError && error.message === 'Failed to fetch') {
                throw new Error('NetworkError: Unable to connect to the server');
            }
            console.error('API Error:', error);
            throw error;
        }
    },

    // Refresh token
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            return false;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${refreshToken}`
                }
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();
            this.setToken(data.access_token);
            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    },

    // Auth endpoints
    auth: {
        async login(email, password) {
            return api.fetch('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
        },

        async register(username, email, password) {
            return api.fetch('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
        },

        async logout() {
            try {
                await api.fetch('/auth/logout', { method: 'POST' });
            } finally {
                // Always clear local storage even if API call fails
                api.removeToken();
            }
        },

        async getProfile() {
            return api.fetch('/auth/me');
        }
    },

    // Task endpoints
    tasks: {
        async getAll(params = {}) {
            const queryParams = new URLSearchParams();
            
            // Add all params to query string
            Object.entries(params).forEach(([key, value]) => {
                if (value !== undefined && value !== null && value !== '') {
                    queryParams.append(key, value);
                }
            });
            
            const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
            return api.fetch(`/tasks${queryString}`);
        },

        async getById(id) {
            return api.fetch(`/tasks/${id}`);
        },

        async create(taskData) {
            return api.fetch('/tasks', {
                method: 'POST',
                body: JSON.stringify(taskData)
            });
        },

        async update(id, taskData) {
            return api.fetch(`/tasks/${id}`, {
                method: 'PUT',
                body: JSON.stringify(taskData)
            });
        },

        async delete(id) {
            return api.fetch(`/tasks/${id}`, {
                method: 'DELETE'
            });
        },

        async getStatistics() {
            return api.fetch('/tasks/statistics');
        }
    },

    // Tag endpoints
    tags: {
        async getAll() {
            return api.fetch('/tags');
        },

        async create(tagData) {
            return api.fetch('/tags', {
                method: 'POST',
                body: JSON.stringify(tagData)
            });
        },

        async update(id, tagData) {
            return api.fetch(`/tags/${id}`, {
                method: 'PUT',
                body: JSON.stringify(tagData)
            });
        },

        async delete(id) {
            return api.fetch(`/tags/${id}`, {
                method: 'DELETE'
            });
        },

        async addToTask(taskId, tagId) {
            return api.fetch(`/tasks/${taskId}/tags`, {
                method: 'POST',
                body: JSON.stringify({ tag_id: tagId })
            });
        },

        async removeFromTask(taskId, tagId) {
            return api.fetch(`/tasks/${taskId}/tags/${tagId}`, {
                method: 'DELETE'
            });
        }
    },

    // Comment endpoints
    comments: {
        async getForTask(taskId) {
            return api.fetch(`/tasks/${taskId}/comments`);
        },

        async create(taskId, content) {
            return api.fetch(`/tasks/${taskId}/comments`, {
                method: 'POST',
                body: JSON.stringify({ content })
            });
        },

        async update(commentId, content) {
            return api.fetch(`/comments/${commentId}`, {
                method: 'PUT',
                body: JSON.stringify({ content })
            });
        },

        async delete(commentId) {
            return api.fetch(`/comments/${commentId}`, {
                method: 'DELETE'
            });
        }
    }
};

// Check if user is already logged in
document.addEventListener('DOMContentLoaded', () => {
    // Redirect to login if not authenticated and not on login/register page
    const isAuthPage = window.location.pathname.includes('login.html') || 
                      window.location.pathname.includes('register.html');
    
    if (!api.isAuthenticated() && !isAuthPage) {
        window.location.href = 'login.html';
    } else if (api.isAuthenticated() && isAuthPage) {
        window.location.href = 'index.html';
    }
});