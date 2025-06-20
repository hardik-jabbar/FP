/**
 * Storage Utility
 * 
 * Provides a wrapper around localStorage/sessionStorage with expiration support
 * and type-safe operations.
 */

const PREFIX = 'farmai_';

export const StorageType = {
  LOCAL: 'local',
  SESSION: 'session',
};

/**
 * Gets the storage instance based on type
 * @param {string} type - Storage type (local or session)
 * @returns {Storage} The storage instance
 */
function getStorage(type = StorageType.LOCAL) {
  if (typeof window === 'undefined') {
    throw new Error('Storage is only available in browser environments');
  }
  
  return type === StorageType.SESSION ? sessionStorage : localStorage;
}

/**
 * Sets an item in storage with optional expiration
 * @param {string} key - The key to store under
 * @param {any} value - The value to store (will be stringified)
 * @param {Object} options - Options object
 * @param {number} options.expiresIn - Time in milliseconds until expiration
 * @param {string} options.type - Storage type (local or session)
 */
export function setItem(key, value, { expiresIn, type = StorageType.LOCAL } = {}) {
  try {
    const storage = getStorage(type);
    const item = {
      value,
      timestamp: Date.now(),
      ...(expiresIn ? { expires: Date.now() + expiresIn } : {}),
    };
    
    storage.setItem(`${PREFIX}${key}`, JSON.stringify(item));
    return true;
  } catch (error) {
    console.error('Error setting storage item:', error);
    return false;
  }
}

/**
 * Gets an item from storage
 * @param {string} key - The key to retrieve
 * @param {Object} options - Options object
 * @param {any} options.defaultValue - Default value if item doesn't exist or is expired
 * @param {string} options.type - Storage type (local or session)
 * @returns {any} The stored value or defaultValue
 */
export function getItem(key, { defaultValue = null, type = StorageType.LOCAL } = {}) {
  try {
    const storage = getStorage(type);
    const itemStr = storage.getItem(`${PREFIX}${key}`);
    
    if (!itemStr) return defaultValue;
    
    const item = JSON.parse(itemStr);
    
    // Check if item is expired
    if (item.expires && Date.now() > item.expires) {
      // Remove expired item
      storage.removeItem(`${PREFIX}${key}`);
      return defaultValue;
    }
    
    return item.value !== undefined ? item.value : defaultValue;
  } catch (error) {
    console.error('Error getting storage item:', error);
    return defaultValue;
  }
}

/**
 * Removes an item from storage
 * @param {string} key - The key to remove
 * @param {Object} options - Options object
 * @param {string} options.type - Storage type (local or session)
 */
export function removeItem(key, { type = StorageType.LOCAL } = {}) {
  try {
    const storage = getStorage(type);
    storage.removeItem(`${PREFIX}${key}`);
    return true;
  } catch (error) {
    console.error('Error removing storage item:', error);
    return false;
  }
}

/**
 * Clears all items with the app's prefix from storage
 * @param {Object} options - Options object
 * @param {string} options.type - Storage type (local or session)
 */
export function clear({ type = StorageType.LOCAL } = {}) {
  try {
    const storage = getStorage(type);
    
    // Only remove keys with our prefix
    Object.keys(storage).forEach(key => {
      if (key.startsWith(PREFIX)) {
        storage.removeItem(key);
      }
    });
    
    return true;
  } catch (error) {
    console.error('Error clearing storage:', error);
    return false;
  }
}

/**
 * Gets all keys in storage with the app's prefix
 * @param {Object} options - Options object
 * @param {string} options.type - Storage type (local or session)
 * @returns {string[]} Array of keys (without prefix)
 */
export function getKeys({ type = StorageType.LOCAL } = {}) {
  try {
    const storage = getStorage(type);
    return Object.keys(storage)
      .filter(key => key.startsWith(PREFIX))
      .map(key => key.substring(PREFIX.length));
  } catch (error) {
    console.error('Error getting storage keys:', error);
    return [];
  }
}

// Convenience methods for common use cases

export const storage = {
  // Session
  setSession: (key, value, options) => 
    setItem(key, value, { ...options, type: StorageType.SESSION }),
  getSession: (key, options) => 
    getItem(key, { ...options, type: StorageType.SESSION }),
  removeSession: (key) => 
    removeItem(key, { type: StorageType.SESSION }),
  clearSession: () => 
    clear({ type: StorageType.SESSION }),
  getSessionKeys: () => 
    getKeys({ type: StorageType.SESSION }),
  
  // Local
  setLocal: setItem,
  getLocal: getItem,
  removeLocal: removeItem,
  clearLocal: clear,
  getLocalKeys: getKeys,
};

export default storage;
