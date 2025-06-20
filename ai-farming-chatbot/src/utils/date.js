/**
 * Date and Time Utilities
 * 
 * Provides functions for working with dates, times, and timezones.
 * Uses the native Intl API for internationalization support.
 */

/**
 * Format a date string, timestamp, or Date object
 * @param {Date|string|number} date - The date to format
 * @param {Object} options - Formatting options
 * @param {string} options.locale - BCP 47 language tag (default: 'en-US')
 * @param {string} options.dateStyle - Date style ('full', 'long', 'medium', 'short')
 * @param {string} options.timeStyle - Time style ('full', 'long', 'medium', 'short')
 * @param {string} options.timeZone - IANA time zone name (e.g., 'America/New_York')
 * @param {boolean} options.relative - Whether to return relative time (e.g., '2 hours ago')
 * @param {number} options.relativeThreshold - Threshold in ms for relative time (default: 1 week)
 * @returns {string} Formatted date string
 */
export function formatDate(
  date,
  {
    locale = 'en-US',
    dateStyle = 'medium',
    timeStyle = 'short',
    timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone,
    relative = false,
    relativeThreshold = 7 * 24 * 60 * 60 * 1000, // 1 week
  } = {}
) {
  if (!date) return '';
  
  const dateObj = date instanceof Date ? date : new Date(date);
  
  // Handle invalid date
  if (Number.isNaN(dateObj.getTime())) {
    return 'Invalid date';
  }
  
  // Handle relative time if enabled and within threshold
  if (relative) {
    const now = new Date();
    const diff = now - dateObj;
    const absDiff = Math.abs(diff);
    
    if (absDiff < relativeThreshold) {
      return getRelativeTime(dateObj, locale);
    }
  }
  
  // Format as absolute date/time
  const formatter = new Intl.DateTimeFormat(locale, {
    dateStyle,
    timeStyle,
    timeZone,
  });
  
  return formatter.format(dateObj);
}

/**
 * Get relative time string (e.g., "2 hours ago")
 * @param {Date} date - The date to compare
 * @param {string} locale - BCP 47 language tag
 * @returns {string} Relative time string
 */
function getRelativeTime(date, locale = 'en-US') {
  const now = new Date();
  const diff = now - date;
  const absDiff = Math.abs(diff);
  
  // Less than a minute
  if (absDiff < 60 * 1000) {
    return 'just now';
  }
  
  // Less than an hour
  if (absDiff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
    return rtf.format(-minutes, 'minute');
  }
  
  // Less than a day
  if (absDiff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
    return rtf.format(-hours, 'hour');
  }
  
  // Less than a week
  if (absDiff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
    return rtf.format(-days, 'day');
  }
  
  // Fall back to absolute date
  return formatDate(date, { locale, dateStyle: 'medium' });
}

/**
 * Format a duration in milliseconds to a human-readable string
 * @param {number} ms - Duration in milliseconds
 * @param {Object} options - Formatting options
 * @param {number} options.precision - Number of units to include (default: 2)
 * @param {boolean} options.compact - Whether to use compact units (e.g., '1h 30m')
 * @returns {string} Formatted duration
 */
export function formatDuration(ms, { precision = 2, compact = false } = {}) {
  if (typeof ms !== 'number' || ms < 0) {
    return '0s';
  }
  
  const timeUnits = [
    { unit: 'day', ms: 24 * 60 * 60 * 1000, compact: 'd' },
    { unit: 'hour', ms: 60 * 60 * 1000, compact: 'h' },
    { unit: 'minute', ms: 60 * 1000, compact: 'm' },
    { unit: 'second', ms: 1000, compact: 's' },
    { unit: 'millisecond', ms: 1, compact: 'ms' },
  ];
  
  const parts = [];
  let remaining = ms;
  
  for (const { unit, ms: unitMs, compact: compactUnit } of timeUnits) {
    if (parts.length >= precision) break;
    
    const value = Math.floor(remaining / unitMs);
    if (value > 0 || (compact && remaining > 0)) {
      parts.push({
        value,
        unit: compact ? compactUnit : unit + (value !== 1 ? 's' : ''),
      });
      remaining %= unitMs;
    }
  }
  
  if (parts.length === 0) {
    return compact ? '0s' : '0 seconds';
  }
  
  return parts
    .slice(0, precision)
    .map(({ value, unit }) => `${value}${compact ? '' : ' '}${unit}`)
    .join(compact ? ' ' : ', ');
}

/**
 * Parse a date string in various formats to a Date object
 * @param {string} dateStr - The date string to parse
 * @returns {Date} Parsed Date object or null if invalid
 */
export function parseDate(dateStr) {
  if (!dateStr) return null;
  
  // Try parsing with Date constructor first
  const date = new Date(dateStr);
  if (!Number.isNaN(date.getTime())) {
    return date;
  }
  
  // Try parsing common formats
  const formats = [
    // ISO 8601
    /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|([+-]\d{2}:?\d{2})?)$/,
    // YYYY-MM-DD
    /^(\d{4})-(\d{2})-(\d{2})$/,
    // MM/DD/YYYY
    /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/,
    // DD.MM.YYYY
    /^(\d{1,2})\.(\d{1,2})\.(\d{4})$/,
  ];
  
  for (const regex of formats) {
    const match = dateStr.match(regex);
    if (match) {
      // Handle different capture groups based on format
      let year, month, day, hours = 0, minutes = 0, seconds = 0;
      
      if (regex === formats[0]) {
        // ISO 8601
        [, year, month, day, hours, minutes, seconds] = match.map(Number);
      } else if (regex === formats[1]) {
        // YYYY-MM-DD
        [, year, month, day] = match.map(Number);
        month -= 1; // JS months are 0-indexed
      } else if (regex === formats[2] || regex === formats[3]) {
        // MM/DD/YYYY or DD.MM.YYYY
        const isUSFormat = regex === formats[2];
        year = parseInt(match[3], 10);
        month = parseInt(match[isUSFormat ? 1 : 2], 10) - 1;
        day = parseInt(match[isUSFormat ? 2 : 1], 10);
      }
      
      const parsedDate = new Date(year, month, day, hours, minutes, seconds);
      if (!Number.isNaN(parsedDate.getTime())) {
        return parsedDate;
      }
    }
  }
  
  return null;
}

/**
 * Get the start of a time period (day, week, month, year)
 * @param {string} period - The period ('day', 'week', 'month', 'year')
 * @param {Date} [date=new Date()] - The reference date
 * @returns {Date} The start of the period
 */
export function startOf(period, date = new Date()) {
  const result = new Date(date);
  
  switch (period.toLowerCase()) {
    case 'year':
      result.setMonth(0, 1);
      result.setHours(0, 0, 0, 0);
      break;
    case 'month':
      result.setDate(1);
      result.setHours(0, 0, 0, 0);
      break;
    case 'week':
      const day = result.getDay();
      const diff = result.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
      result.setDate(diff);
      result.setHours(0, 0, 0, 0);
      break;
    case 'day':
    default:
      result.setHours(0, 0, 0, 0);
      break;
  }
  
  return result;
}

/**
 * Get the end of a time period (day, week, month, year)
 * @param {string} period - The period ('day', 'week', 'month', 'year')
 * @param {Date} [date=new Date()] - The reference date
 * @returns {Date} The end of the period
 */
export function endOf(period, date = new Date()) {
  const result = new Date(date);
  
  switch (period.toLowerCase()) {
    case 'year':
      result.setFullYear(result.getFullYear() + 1, 0, 1);
      result.setHours(0, 0, 0, 0);
      result.setMilliseconds(-1);
      break;
    case 'month':
      result.setMonth(result.getMonth() + 1, 1);
      result.setHours(0, 0, 0, 0);
      result.setMilliseconds(-1);
      break;
    case 'week':
      const day = result.getDay();
      const diff = result.getDate() - day + (day === 0 ? 0 : 7); // Next Sunday
      result.setDate(diff);
      result.setHours(23, 59, 59, 999);
      break;
    case 'day':
    default:
      result.setHours(23, 59, 59, 999);
      break;
  }
  
  return result;
}

/**
 * Check if a date is today
 * @param {Date} date - The date to check
 * @returns {boolean} True if the date is today
 */
export function isToday(date) {
  if (!(date instanceof Date)) return false;
  
  const today = new Date();
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

/**
 * Check if a date is in the past
 * @param {Date} date - The date to check
 * @returns {boolean} True if the date is in the past
 */
export function isPast(date) {
  if (!(date instanceof Date)) return false;
  return date < new Date();
}

/**
 * Check if a date is in the future
 * @param {Date} date - The date to check
 * @returns {boolean} True if the date is in the future
 */
export function isFuture(date) {
  if (!(date instanceof Date)) return false;
  return date > new Date();
}

// Export all functions as default for easier importing
export default {
  formatDate,
  formatDuration,
  parseDate,
  startOf,
  endOf,
  isToday,
  isPast,
  isFuture,
};
