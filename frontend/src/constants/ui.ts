/**
 * UI timing constants used across the app.
 *
 * Extract magic numbers to named constants for clarity and consistency.
 */

/** Debounce delay for search/filter inputs (ms) */
export const DEBOUNCE_SEARCH_MS = 300

/** Debounce delay for rapid state changes like calendar navigation (ms) */
export const DEBOUNCE_FETCH_MS = 50

/** Delay before enabling flatpickr inputs after mount (ms) */
export const FLATPICKR_READY_DELAY_MS = 50

/** Auto-hide duration for success/info messages (ms) */
export const SUCCESS_MESSAGE_TIMEOUT_MS = 8000

/** Max number of page-view cache entries before eviction */
export const MAX_PAGE_VIEW_CACHE_SIZE = 100

/** Max file size for icon uploads (512 KB) */
export const MAX_ICON_FILE_SIZE_BYTES = 512 * 1024
