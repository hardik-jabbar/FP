/**
 * Utility Module Exports
 * 
 * Central export point for all utility functions.
 */

// API utilities
export * from './api';

// Date and time utilities
export * from './date';

// String manipulation utilities
export * from './string';

// Storage utilities
export * from './storage';

// Re-export all utilities as a default object
import * as api from './api';
import * as date from './date';
import * as string from './string';
import * as storage from './storage';

const utils = {
  api,
  date,
  string,
  storage,
};

export default utils;
