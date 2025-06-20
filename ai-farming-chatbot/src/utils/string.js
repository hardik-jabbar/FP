/**
 * String Utilities
 * 
 * Provides common string manipulation and validation functions.
 */

/**
 * Truncates a string to a specified length and adds an ellipsis if truncated
 * @param {string} str - The string to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @param {string} [ellipsis='...'] - The ellipsis string to append
 * @returns {string} The truncated string
 */
export function truncate(str, maxLength, ellipsis = '...') {
  if (typeof str !== 'string') return '';
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength) + ellipsis;
}

/**
 * Converts a string to title case
 * @param {string} str - The string to convert
 * @returns {string} The title-cased string
 */
export function toTitleCase(str) {
  if (typeof str !== 'string') return '';
  return str.replace(
    /\w\S*/g,
    txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
}

/**
 * Converts a string to kebab-case
 * @param {string} str - The string to convert
 * @returns {string} The kebab-cased string
 */
export function toKebabCase(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

/**
 * Converts a string to camelCase
 * @param {string} str - The string to convert
 * @returns {string} The camelCased string
 */
export function toCamelCase(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/(?:^\w|[A-Z]|\b\w)/g, (word, index) => 
      index === 0 ? word.toLowerCase() : word.toUpperCase()
    )
    .replace(/[\s-]+/g, '');
}

/**
 * Converts a string to PascalCase
 * @param {string} str - The string to convert
 * @returns {string} The PascalCased string
 */
export function toPascalCase(str) {
  if (typeof str !== 'string') return '';
  return str
    .match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

/**
 * Converts a string to snake_case
 * @param {string} str - The string to convert
 * @returns {string} The snake_cased string
 */
export function toSnakeCase(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase();
}

/**
 * Removes all whitespace from a string
 * @param {string} str - The string to process
 * @returns {string} The string without whitespace
 */
export function removeWhitespace(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/\s+/g, '');
}

/**
 * Checks if a string is a valid email address
 * @param {string} email - The email to validate
 * @returns {boolean} True if the email is valid
 */
export function isValidEmail(email) {
  if (typeof email !== 'string') return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Checks if a string is a valid URL
 * @param {string} url - The URL to validate
 * @returns {boolean} True if the URL is valid
 */
export function isValidUrl(url) {
  if (typeof url !== 'string') return false;
  try {
    new URL(url);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Generates a random string of specified length
 * @param {number} length - The length of the random string
 * @param {string} [charset='alphanumeric'] - The character set to use ('alphanumeric', 'alphabetic', 'numeric', 'hex')
 * @returns {string} The random string
 */
export function randomString(
  length = 10,
  charset = 'alphanumeric'
) {
  let chars = '';
  
  switch (charset) {
    case 'alphabetic':
      chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
      break;
    case 'numeric':
      chars = '0123456789';
      break;
    case 'hex':
      chars = '0123456789abcdef';
      break;
    case 'alphanumeric':
    default:
      chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      break;
  }
  
  let result = '';
  const charsLength = chars.length;
  
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * charsLength));
  }
  
  return result;
}

/**
 * Escapes a string for use in a regular expression
 * @param {string} str - The string to escape
 * @returns {string} The escaped string
 */
export function escapeRegExp(str) {
  if (typeof str !== 'string') return '';
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Replaces all occurrences of a substring in a string
 * @param {string} str - The string to perform replacements on
 * @param {string} search - The substring to search for
 * @param {string} replace - The replacement string
 * @returns {string} The string with replacements
 */
export function replaceAll(str, search, replace) {
  if (typeof str !== 'string') return '';
  return str.split(search).join(replace);
}

/**
 * Counts the number of words in a string
 * @param {string} str - The string to count words in
 * @returns {number} The word count
 */
export function countWords(str) {
  if (typeof str !== 'string') return 0;
  return str.trim() === '' ? 0 : str.trim().split(/\s+/).length;
}

/**
 * Counts the number of characters in a string (supports Unicode)
 * @param {string} str - The string to count characters in
 * @returns {number} The character count
 */
export function countChars(str) {
  if (typeof str !== 'string') return 0;
  return [...str].length;
}

/**
 * Converts a string to a URL-friendly slug
 * @param {string} str - The string to convert
 * @param {string} [separator='-'] - The separator to use
 * @returns {string} The URL-friendly slug
 */
export function toSlug(str, separator = '-') {
  if (typeof str !== 'string') return '';
  
  return str
    .toString()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9 ]/g, '') // Remove non-alphanumeric characters
    .replace(/\s+/g, separator) // Replace spaces with separator
    .replace(new RegExp(`[${escapeRegExp(separator)}]+`, 'g'), separator); // Remove duplicate separators
}

/**
 * Checks if a string starts with a substring (case-insensitive)
 * @param {string} str - The string to check
 * @param {string} search - The substring to search for
 * @returns {boolean} True if the string starts with the substring
 */
export function startsWithIgnoreCase(str, search) {
  if (typeof str !== 'string' || typeof search !== 'string') return false;
  return str.toLowerCase().startsWith(search.toLowerCase());
}

/**
 * Checks if a string ends with a substring (case-insensitive)
 * @param {string} str - The string to check
 * @param {string} search - The substring to search for
 * @returns {boolean} True if the string ends with the substring
 */
export function endsWithIgnoreCase(str, search) {
  if (typeof str !== 'string' || typeof search !== 'string') return false;
  return str.toLowerCase().endsWith(search.toLowerCase());
}

/**
 * Checks if a string contains a substring (case-insensitive)
 * @param {string} str - The string to check
 * @param {string} search - The substring to search for
 * @returns {boolean} True if the string contains the substring
 */
export function includesIgnoreCase(str, search) {
  if (typeof str !== 'string' || typeof search !== 'string') return false;
  return str.toLowerCase().includes(search.toLowerCase());
}

// Export all functions as default for easier importing
export default {
  truncate,
  toTitleCase,
  toKebabCase,
  toCamelCase,
  toPascalCase,
  toSnakeCase,
  removeWhitespace,
  isValidEmail,
  isValidUrl,
  randomString,
  escapeRegExp,
  replaceAll,
  countWords,
  countChars,
  toSlug,
  startsWithIgnoreCase,
  endsWithIgnoreCase,
  includesIgnoreCase,
};
