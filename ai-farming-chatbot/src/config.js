/**
 * Application Configuration
 * 
 * This file centralizes all configuration settings for the application.
 * Values can be overridden by environment variables (prefixed with VITE_ for client-side).
 */

// Environment variables (Vite exposes VITE_* variables)
const ENV = import.meta.env;

// Base configuration
const baseConfig = {
  // App metadata
  app: {
    name: ENV.VITE_APP_NAME || 'FarmAI Assistant',
    description: ENV.VITE_APP_DESCRIPTION || 'AI-powered farming assistant',
    version: '1.0.0',
  },
  
  // API Configuration
  api: {
    baseUrl: ENV.VITE_API_BASE_URL || '/api',
    timeout: 30000,
    maxRetries: 3,
    retryDelay: 1000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  },
  
  // Chat Configuration
  chat: {
    maxHistory: 50,
    maxMessageLength: 2000,
    typingIndicatorDuration: 1000,
    sessionExpiration: 24 * 60 * 60 * 1000, // 24 hours
    suggestions: [
      'How do I improve my crop yield?',
      'What are the best practices for organic farming?',
      'How to prevent common plant diseases?',
      'What crops are best for my region?',
    ],
  },
  
  // UI Configuration
  ui: {
    theme: {
      primary: {
        50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0',
        300: '#86efac', 400: '#4ade80', 500: '#22c55e',
        600: '#16a34a', 700: '#15803d', 800: '#166534',
        900: '#14532d',
      },
      gray: {
        50: '#f9fafb', 100: '#f3f4f6', 200: '#e5e7eb',
        300: '#d1d5db', 400: '#9ca3af', 500: '#6b7280',
        600: '#4b5563', 700: '#374151', 800: '#1f2937',
        900: '#111827',
      },
    },
    layout: {
      headerHeight: '64px',
      footerHeight: '60px',
      maxContentWidth: '1280px',
      animation: {
        fast: 150,
        normal: 300,
        slow: 500,
      },
    },
    breakpoints: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    },
  },
  
  // Feature flags
  features: {
    typingIndicators: true,
    readReceipts: true,
    suggestions: true,
    persistence: true,
    analytics: !!ENV.VITE_GA_TRACKING_ID,
    errorTracking: !!ENV.VITE_SENTRY_DSN,
    offlineSupport: true,
  },
  
  // Analytics configuration
  analytics: {
    googleAnalytics: {
      trackingId: ENV.VITE_GA_TRACKING_ID || '',
    },
  },
  
  // Error tracking
  errorTracking: {
    sentry: {
      dsn: ENV.VITE_SENTRY_DSN || '',
      environment: ENV.MODE || 'development',
    },
  },
  
  // Localization
  i18n: {
    defaultLanguage: 'en',
    languages: [
      { code: 'en', name: 'English' },
      { code: 'es', name: 'Español' },
      { code: 'fr', name: 'Français' },
    ],
  },
  
  // Environment information
  env: {
    isDevelopment: ENV.DEV,
    isProduction: ENV.PROD,
    mode: ENV.MODE,
  },
};

// Helper methods
const helpers = {
  get isDevelopment() {
    return this.env.isDevelopment;
  },
  get isProduction() {
    return this.env.isProduction;
  },
  getThemeColor(name, shade = 500) {
    return this.ui.theme[name]?.[shade] || `var(--${name}-${shade})`;
  },
  getApiUrl(path = '') {
    const base = this.api.baseUrl.replace(/\/$/, '');
    const normalizedPath = path.startsWith('/') ? path : `/${path}`;
    return `${base}${normalizedPath}`;
  },
};

// Create final config by merging base config with helpers
const config = {
  ...baseConfig,
  ...helpers,
};

// Environment-specific overrides
if (import.meta.env.DEV) {
  config.api.baseUrl = 'http://localhost:5000/api';
}

export default config;
