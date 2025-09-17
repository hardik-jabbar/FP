import { supabase } from './supabase-config.js';

class Auth {
    async registerUser(formData) {
        try {
            const { data, error } = await supabase.auth.signUp({
                email: formData.email,
                password: formData.password,
                options: {
                    data: {
                        firstName: formData.firstName,
                        lastName: formData.lastName,
                        farmType: formData.farmType
                    }
                }
            });

            if (error) throw error;

            // Create profile record
            if (data.user) {
                const { error: profileError } = await supabase
                    .from('profiles')
                    .insert([
                        {
                            user_id: data.user.id,
                            first_name: formData.firstName,
                            last_name: formData.lastName,
                            email: formData.email,
                            farm_type: formData.farmType
                        }
                    ]);

                if (profileError) throw profileError;
            }

            return data;
        } catch (error) {
            console.error('Registration error:', error);
            throw new Error(error.message);
        }
    }

    async loginUser({ email, password }) {
        try {
            const { data, error } = await supabase.auth.signInWithPassword({
                email,
                password
            });

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw new Error(error.message);
        }
    }

    async verifyOTP(email, token) {
        try {
            const { data, error } = await supabase.auth.verifyOtp({
                email,
                token,
                type: 'signup'
            });

            if (error) throw error;
            return data;
        } catch (error) {
            console.error('OTP verification error:', error);
            throw new Error(error.message);
        }
    }

    async logoutUser() {
        try {
            const { error } = await supabase.auth.signOut();
            if (error) throw error;
            window.location.href = 'login.html';
        } catch (error) {
            console.error('Logout error:', error);
            throw new Error(error.message);
        }
    }

    async getUserProfile() {
        try {
            const { data: { user }, error: userError } = await supabase.auth.getUser();
            
            if (userError) throw userError;
            if (!user) throw new Error('No user found');

            const { data, error } = await supabase
                .from('profiles')
                .select('*')
                .eq('user_id', user.id)
                .single();

            if (error) throw error;

            return {
                firstName: data.first_name,
                lastName: data.last_name,
                email: data.email,
                farmType: data.farm_type,
                equipmentCount: data.equipment_count || 0,
                activeServices: data.active_services || 0,
                notifications: data.notifications || 0,
                recentActivity: data.recent_activity || []
            };
        } catch (error) {
            console.error('Get profile error:', error);
            throw new Error('Failed to fetch user profile');
        }
    }

    async isAuthenticated() {
        try {
            const { data: { session }, error } = await supabase.auth.getSession();
            if (error) throw error;
            return !!session;
        } catch (error) {
            console.error('Auth check error:', error);
            return false;
        }
    }
}

const auth = new Auth();
export default auth;
