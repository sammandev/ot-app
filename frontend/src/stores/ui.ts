/**
 * UI Store
 * Manages UI state: sidebar, theme, notifications
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
	// Sidebar state
	const sidebarExpanded = ref(false)
	const sidebarHidden = ref(false)
	const sidebarMobileOpen = ref(false)
	const sidebarHovered = ref(false)
	const activeMenuItem = ref<string | null>(null)
	const openSubmenu = ref<string | null>(null)

	// Theme state
	const isDarkMode = ref(false)

	// Date filter state (shared across Overtime Summary, Employee/Project Overtime pages)
	interface DateFilterState {
		selectionType: 'year-month' | 'custom'
		selectedYear: number
		selectedMonth: string | number
		customDateRange: string
	}

	// Calculate current period month/year based on 26th-25th cycle
	// e.g. Dec 26 – Jan 25 = January period; Jan 26 – Feb 25 = February period
	const _getCurrentPeriod = () => {
		const today = new Date()
		if (today.getDate() >= 26) {
			// On or after the 26th → next month's period
			const end = new Date(today)
			end.setMonth(end.getMonth() + 1, 25)
			return { year: end.getFullYear(), month: end.getMonth() + 1 }
		}
		// Before the 26th → current calendar month's period
		return { year: today.getFullYear(), month: today.getMonth() + 1 }
	}
	const _defaultPeriod = _getCurrentPeriod()

	const dateFilter = ref<DateFilterState>({
		selectionType: 'year-month',
		selectedYear: _defaultPeriod.year,
		selectedMonth: _defaultPeriod.month,
		customDateRange: '',
	})

	// Toast notifications
	interface Toast {
		id: string
		message: string
		type: 'success' | 'error' | 'info' | 'warning'
		duration?: number
	}
	const toasts = ref<Toast[]>([])
	const _toastTimers = new Map<string, ReturnType<typeof setTimeout>>()

	// Initialize from localStorage
	const initFromStorage = () => {
		try {
			const hidden = localStorage.getItem('sidebarHidden')
			sidebarHidden.value = hidden === '1'

			const expanded = localStorage.getItem('sidebarExpanded')
			if (expanded !== null && !sidebarHidden.value) {
				sidebarExpanded.value = expanded === '1'
			}

			const theme = localStorage.getItem('theme')
			isDarkMode.value = theme === 'dark'
			if (isDarkMode.value) {
				document.documentElement.classList.add('dark')
			}

			// Load date filter state from localStorage
			const savedDateFilter = localStorage.getItem('overtimeDateFilter')
			if (savedDateFilter) {
				try {
					const parsed = JSON.parse(savedDateFilter)
					const fallback = _getCurrentPeriod()
					dateFilter.value = {
						selectionType: parsed.selectionType || 'year-month',
						selectedYear: parsed.selectedYear || fallback.year,
						selectedMonth: parsed.selectedMonth ?? fallback.month,
						customDateRange: parsed.customDateRange || '',
					}
				} catch {
					// Keep defaults if parsing fails
				}
			}
		} catch (error) {
			console.error('Error loading UI state from localStorage:', error)
		}
	}

	// Sidebar actions
	const toggleSidebar = () => {
		if (sidebarHidden.value) {
			sidebarHidden.value = false
			sidebarExpanded.value = true
			localStorage.setItem('sidebarHidden', '0')
			localStorage.setItem('sidebarExpanded', '1')
		} else {
			sidebarHidden.value = true
			localStorage.setItem('sidebarHidden', '1')
		}
	}

	const toggleSidebarExpanded = () => {
		if (!sidebarHidden.value) {
			sidebarExpanded.value = !sidebarExpanded.value
			localStorage.setItem('sidebarExpanded', sidebarExpanded.value ? '1' : '0')
		}
	}

	const toggleMobileSidebar = () => {
		sidebarMobileOpen.value = !sidebarMobileOpen.value
	}

	const setSidebarHovered = (hovered: boolean) => {
		sidebarHovered.value = hovered
	}

	const setActiveMenuItem = (item: string | null) => {
		activeMenuItem.value = item
	}

	const toggleSubmenu = (item: string) => {
		openSubmenu.value = openSubmenu.value === item ? null : item
	}

	// Theme actions
	const toggleTheme = () => {
		isDarkMode.value = !isDarkMode.value
		localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
		if (isDarkMode.value) {
			document.documentElement.classList.add('dark')
		} else {
			document.documentElement.classList.remove('dark')
		}
	}

	const setTheme = (dark: boolean) => {
		isDarkMode.value = dark
		localStorage.setItem('theme', dark ? 'dark' : 'light')
		if (dark) {
			document.documentElement.classList.add('dark')
		} else {
			document.documentElement.classList.remove('dark')
		}
	}

	// Toast actions
	const addToast = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
		const id = `toast-${Date.now()}-${Math.round(Math.random() * 1000)}`
		const toast: Toast = { id, message, type, duration }
		toasts.value.push(toast)

		if (duration > 0) {
			const timer = setTimeout(() => {
				removeToast(id)
			}, duration)
			_toastTimers.set(id, timer)
		}

		return id
	}

	const removeToast = (id: string) => {
		const timer = _toastTimers.get(id)
		if (timer) {
			clearTimeout(timer)
			_toastTimers.delete(id)
		}
		const index = toasts.value.findIndex((t) => t.id === id)
		if (index > -1) {
			toasts.value.splice(index, 1)
		}
	}

	const clearToasts = () => {
		for (const timer of _toastTimers.values()) {
			clearTimeout(timer)
		}
		_toastTimers.clear()
		toasts.value = []
	}

	// Date filter actions
	const setDateFilter = (filter: Partial<DateFilterState>) => {
		dateFilter.value = { ...dateFilter.value, ...filter }
		localStorage.setItem('overtimeDateFilter', JSON.stringify(dateFilter.value))
	}

	const resetDateFilter = () => {
		const period = _getCurrentPeriod()
		dateFilter.value = {
			selectionType: 'year-month',
			selectedYear: period.year,
			selectedMonth: period.month,
			customDateRange: '',
		}
		localStorage.setItem('overtimeDateFilter', JSON.stringify(dateFilter.value))
	}

	// Computed
	const isSidebarVisible = computed(() => !sidebarHidden.value)

	return {
		// State
		sidebarExpanded,
		sidebarHidden,
		sidebarMobileOpen,
		sidebarHovered,
		activeMenuItem,
		openSubmenu,
		isDarkMode,
		toasts,
		dateFilter,

		// Computed
		isSidebarVisible,

		// Actions
		initFromStorage,
		toggleSidebar,
		toggleSidebarExpanded,
		toggleMobileSidebar,
		setSidebarHovered,
		setActiveMenuItem,
		toggleSubmenu,
		toggleTheme,
		setTheme,
		addToast,
		removeToast,
		clearToasts,
		setDateFilter,
		resetDateFilter,
	}
})
