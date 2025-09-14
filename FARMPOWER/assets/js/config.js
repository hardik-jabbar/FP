// API Configuration
const config = {
    api: {
        baseUrl: process.env.NODE_ENV === 'production' 
            ? 'https://fp-mipu.onrender.com'  // Production API URL
            : 'http://localhost:8000',         // Development API URL
    }
};

export default config;