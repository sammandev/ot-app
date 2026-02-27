/**
 * Centralized localStorage key constants.
 *
 * All localStorage keys used across the app should be defined here
 * to prevent key collisions and ease refactoring.
 */

// Authentication
export const STORAGE_KEY_REMEMBER_ME = 'rememberMe'

// UI / Theme
export const STORAGE_KEY_THEME = 'theme'
export const STORAGE_KEY_SIDEBAR_HIDDEN = 'sidebarHidden'
export const STORAGE_KEY_SIDEBAR_EXPANDED = 'sidebarExpanded'

// Calendar
export const STORAGE_KEY_CALENDAR_THEME = 'calendar_theme'
export const STORAGE_KEY_CALENDAR_VIEW = 'calendarView'
export const STORAGE_KEY_PTB_CALENDAR_VIEW_MODE = 'ptb-calendar-view-mode'
export const STORAGE_KEY_PTB_CALENDAR_YEAR_TABS = 'ptb-calendar-year-tabs'

// Admin
export const STORAGE_KEY_SUPERADMIN_TAB = 'superadmin_tab'

// Overtime
export const STORAGE_KEY_OVERTIME_DATE_FILTER = 'overtimeDateFilter'
export const STORAGE_KEY_HIDE_OVERTIME_INFO = 'hideOvertimeInfoCard'
export const STORAGE_KEY_OVERTIME_REGS_COLLAPSED = 'overtimeRegulationsCollapsed'
export const STORAGE_KEY_OT_POLICY_DOCUMENT = 'ot_policy_document'

// Localization
export const STORAGE_KEY_LOCALE = 'app_locale'

// Reminders
export const STORAGE_KEY_DISMISSED_REMINDERS = 'dismissed_reminders'
export const STORAGE_KEY_SNOOZE_SETTINGS = 'snooze_settings'
export const STORAGE_KEY_DISMISSED_REMINDERS_DATE = 'dismissed_reminders_date'
