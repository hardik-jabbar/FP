// Authentication service for FarmPower using Supabase
const SUPABASE_URL = 'https://fmqxdoocmapllbuecblc.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtcXhkb29jbWFwbGxidWVjYmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTQ2NjUyMjYsImV4cCI6MjAxMDI0MTIyNn0.Fk1PiWHtCiCWus6nhgVrF_n7LSt9G5VuhDCCXYFPqE4';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Make auth available globally
window.auth = {
    // Check if user is authenticated
    isAuthenticated() {
        return !!supabase.auth.getSession();
    },

    // Register a new user
    async registerUser(userData) {
        try {
            // If only email provided, treat as OTP request
            const isOtpRequest = Object.keys(userData).length === 1 && userData.email;
            
            if (isOtpRequest) {
                // Handle OTP request through custom backend if needed
                throw new Error('OTP functionality not implemented');
            }

            // Register user with Supabase
            const { data, error } = await supabase.auth.signUp({
                email: userData.email,
                password: userData.password,
                options: {
                    data: {
                        full_name: `${userData.firstName} ${userData.lastName}`,
                        role: 'FARMER',
                        farm_type: userData.farmType,
                        terms_accepted: userData.terms
                    }
                }
            });

            if (error) throw error;

            // Create user profile in Supabase database
            const { error: profileError } = await supabase
                .from('profiles')
                .insert([
                    {
                        id: data.user.id,
                        full_name: `${userData.firstName} ${userData.lastName}`,
                        email: userData.email,
                        role: 'FARMER',
                        farm_type: userData.farmType,
                        terms_accepted: userData.terms,
                        is_active: true
                    }
                ]);

            if (profileError) throw profileError;

            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    },

    // Login user
    async loginUser(credentials) {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email: credentials.email,
                password: credentials.password,
            });

            if (error) throw error;

            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    },

        // Get user profile
    async getUserProfile() {
        try {
            const { data: { user } } = await supabase.auth.getUser();
            
            if (!user) throw new Error('No user found');

            const { data: profile, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('id', user.id)
                .single();

            if (error) throw error;
            
            return profile;
        } catch (error) {
            console.error('Get profile error:', error);
            throw error;
        }
    },

    // Sign out
    async signOut() {
        try {
            const { error } = await supabase.auth.signOut();
            if (error) throw error;
        } catch (error) {
            console.error('Sign out error:', error);
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