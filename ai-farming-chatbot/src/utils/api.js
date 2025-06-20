/**
 * API Utility Module
 * 
 * Provides a wrapper around fetch with automatic retries, timeouts, and error handling.
 * Also includes methods for common API operations.
 */

import config from '../config';

// Custom error class for API errors
class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
    this.isApiError = true;
  }
}

/**
 * Performs a fetch request with retries and timeout
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options
 * @param {number} retries - Number of retries remaining
 * @returns {Promise<Response>} - The fetch response
 */
async function fetchWithRetry(url, options = {}, retries = config.api.maxRetries) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), config.api.timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    
    clearTimeout(timeoutId);
    
    // If the response is not ok, throw an error
    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json().catch(() => ({}));
      } catch (e) {
        errorData = { message: 'Unknown error occurred' };
      }
      
      throw new ApiError(
        errorData.message || response.statusText,
        response.status,
        errorData
      );
    }
    
    return response;
    
  } catch (error) {
    clearTimeout(timeoutId);
    
    // If the error is an AbortError due to timeout, and we have retries left, retry
    if (
      (error.name === 'AbortError' || 
       error.name === 'TypeError' || // Network errors
       (error.status >= 500 && error.status < 600)) && // Server errors
      retries > 0
    ) {
      // Wait for the retry delay before retrying
      await new Promise(resolve => 
        setTimeout(resolve, config.api.retryDelay * (config.api.maxRetries - retries + 1))
      );
      
      return fetchWithRetry(url, options, retries - 1);
    }
    
    // If we're out of retries or the error is not retryable, rethrow
    throw error;
  }
}

/**
 * Performs a GET request
 * @param {string} endpoint - The API endpoint (without base URL)
 * @param {Object} params - Query parameters
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - The parsed JSON response
 */
export async function get(endpoint, params = {}, options = {}) {
  const queryString = new URLSearchParams(params).toString();
  const url = `${config.api.baseUrl}${endpoint}${queryString ? `?${queryString}` : ''}`;
  
  const response = await fetchWithRetry(url, {
    ...options,
    method: 'GET',
  });
  
  return response.json();
}

/**
 * Performs a POST request
 * @param {string} endpoint - The API endpoint (without base URL)
 * @param {Object} data - The request body
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - The parsed JSON response
 */
export async function post(endpoint, data = {}, options = {}) {
  const response = await fetchWithRetry(`${config.api.baseUrl}${endpoint}`, {
    ...options,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    body: JSON.stringify(data),
  });
  
  return response.json();
}

/**
 * Performs a PUT request
 * @param {string} endpoint - The API endpoint (without base URL)
 * @param {Object} data - The request body
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - The parsed JSON response
 */
export async function put(endpoint, data = {}, options = {}) {
  const response = await fetchWithRetry(`${config.api.baseUrl}${endpoint}`, {
    ...options,
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    body: JSON.stringify(data),
  });
  
  return response.json();
}

/**
 * Performs a DELETE request
 * @param {string} endpoint - The API endpoint (without base URL)
 * @param {Object} options - Additional fetch options
 * @returns {Promise<any>} - The parsed JSON response
 */
export async function del(endpoint, options = {}) {
  const response = await fetchWithRetry(`${config.api.baseUrl}${endpoint}`, {
    ...options,
    method: 'DELETE',
  });
  
  // If the response has no content, return null
  if (response.status === 204) {
    return null;
  }
  
  return response.json();
}

/**
 * Uploads a file using FormData
 * @param {string} endpoint - The API endpoint (without base URL)
 * @param {File} file - The file to upload
 * @param {Object} additionalData - Additional form data to include
 * @param {Function} onProgress - Progress callback
 * @returns {Promise<any>} - The parsed JSON response
 */
export async function uploadFile(endpoint, file, additionalData = {}, onProgress = null) {
  const formData = new FormData();
  formData.append('file', file);
  
  // Append additional data to form data
  Object.entries(additionalData).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      formData.append(key, value);
    }
  });
  
  const xhr = new XMLHttpRequest();
  
  return new Promise((resolve, reject) => {
    xhr.open('POST', `${config.api.baseUrl}${endpoint}`);
    
    // Set up progress tracking
    if (onProgress) {
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded * 100) / event.total);
          onProgress(percentComplete);
        }
      };
    }
    
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = xhr.responseText ? JSON.parse(xhr.responseText) : null;
          resolve(response);
        } catch (error) {
          reject(new Error('Failed to parse response'));
        }
      } else {
        let errorData;
        try {
          errorData = xhr.responseText ? JSON.parse(xhr.responseText) : {};
        } catch (e) {
          errorData = { message: 'Unknown error occurred' };
        }
        
        const error = new ApiError(
          errorData.message || xhr.statusText,
          xhr.status,
          errorData
        );
        reject(error);
      }
    };
    
    xhr.onerror = () => {
      reject(new Error('Network error occurred'));
    };
    
    xhr.send(formData);
  });
}

// Export the custom error class
export { ApiError };
