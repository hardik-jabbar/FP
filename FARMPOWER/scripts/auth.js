// Authentication utility functions
const API_BASE_URL = 'http://localhost:8000'; // Update with your FastAPI backend URL

// Store JWT token
const setToken = (token) => {
    localStorage.setItem('token', token);
};

// Get JWT token
const getToken = () => {
    return localStorage.getItem('token');
};

// Remove JWT token
const removeToken = () => {
    localStorage.removeItem('token');
};

// Check if user is authenticated
const isAuthenticated = () => {
    return !!getToken();
};

// Get user profile
const getUserProfile = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
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
};

// Register user
const registerUser = async (userData) => {
    // If only email provided, treat as OTP resend
    const isOtpResend = Object.keys(userData).length === 1 && userData.email;
    let endpoint = isOtpResend ? '/users/request-verification-otp' : '/users/register';

    // Transform fields for backend if full registration
    if (!isOtpResend) {
        userData = {
            email: userData.email,
            password: userData.password,
            full_name: `${userData.firstName} ${userData.lastName}`,
            role: 'farmer' // default role; adjust if needed
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
};

// Login user
const loginUser = async (credentials) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(credentials)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        setToken(data.access_token);
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