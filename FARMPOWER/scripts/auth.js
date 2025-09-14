// Authentication service for FarmPower
const API_BASE_URL = 'https://fp-mipu.onrender.com/api/v1';

const auth = {
    // Store the token in localStorage
    setToken(token) {
        localStorage.setItem('token', token);
    },

    // Get the stored token
    getToken() {
        return localStorage.getItem('token');
    },

    // Clear the stored token
    removeToken() {
        localStorage.removeItem('token');
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    },

    // Register a new user
    async registerUser(userData) {
        // If only email provided, treat as OTP request
        const isOtpRequest = Object.keys(userData).length === 1 && userData.email;
        let endpoint = isOtpRequest ? '/users/request-otp' : '/users/register';

        // Transform fields for backend if full registration
        if (!isOtpRequest) {
            userData = {
                email: userData.email,
                password: userData.password,
                full_name: `${userData.firstName} ${userData.lastName}`,
                role: 'FARMER',
                farm_type: userData.farmType,
                terms_accepted: userData.terms
            };
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Registration failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    // Login user
    async loginUser(credentials) {
        try {
            // Convert credentials to form data for OAuth2 compatibility
            const formData = new URLSearchParams();
            formData.append('username', credentials.email);
            formData.append('password', credentials.password);

            const response = await fetch(`${API_BASE_URL}/users/login/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            this.setToken(data.access_token);
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

    // Get user profile
    async getUserProfile() {
        try {
            const response = await fetch(`${API_BASE_URL}/users/me`, {
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch user profile');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    },

    // Verify OTP
    async verifyOTP(email, otp) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/verify-otp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, otp })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'OTP verification failed');
            }

            return await response.json();
        } catch (error) {
            console.error('OTP verification error:', error);
            throw error;
        }
    }
};

// Export the auth object
window.auth = auth;
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
};

// Verify OTP
const verifyOTP = async (email, otp) => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/verify-otp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, otp })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'OTP verification failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('OTP verification error:', error);
        throw error;
    }
};

// Logout user
const logoutUser = () => {
    removeToken();
    window.location.href = '/login.html';
};

// Export functions
window.auth = {
    setToken,
    getToken,
    removeToken,
    isAuthenticated,
    getUserProfile,
    registerUser,
    loginUser,
    verifyOTP,
    logoutUser
}; 