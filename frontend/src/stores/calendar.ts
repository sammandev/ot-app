/**
 * Calendar Store
 * Manages calendar events and view state
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { type CalendarEvent, calendarAPI } from '@/services/api/calendar'
import { extractApiError } from '@/utils/extractApiError'

interface CalendarView {
	currentView: 'dayGridMonth' | 'timeGridWeek' | 'timeGridDay' | 'listWeek'
	currentDate: string
}

export const useCalendarStore = defineStore('calendar', () => {
	// State
	const events = ref<CalendarEvent[]>([])
	const currentEvent = ref<CalendarEvent | null>(null)
	const loading = ref(false)
	const error = ref<string | null>(null)
	const lastFetch = ref<number | null>(null)

	// Track cached date-range to bust when params change
	const lastFetchStart = ref<string | undefined>(undefined)
	const lastFetchEnd = ref<string | undefined>(undefined)

	// View state
	const view = ref<CalendarView>({
		currentView: 'dayGridMonth',
		currentDate: new Date().toISOString().split('T')[0] || '',
	})

	// Cache duration: 5 minutes
	const CACHE_DURATION = 5 * 60 * 1000

	// Computed
	const upcomingEvents = computed(() => {
		const nowMs = Date.now()
		return events.value
			.filter((event) => new Date(event.start).getTime() > nowMs)
			.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())
			.slice(0, 10)
	})

	const todayEvents = computed(() => {
		const today = new Date().toISOString().split('T')[0]
		if (!today) return []
		return events.value.filter((event) => event.start?.startsWith(today))
	})

	const getEventById = computed(() => {
		return (id: number) => events.value.find((event) => event.id === id)
	})

	const getEventsByEmployee = computed(() => {
		return (employeeId: number) => events.value.filter((event) => event.employee === employeeId)
	})

	const getEventsByProject = computed(() => {
		return (projectId: number) => events.value.filter((event) => event.project === projectId)
	})

	const getEventsByDateRange = computed(() => {
		return (start: string, end: string) => {
			return events.value.filter((event) => {
				const eventStart = new Date(event.start)
				const rangeStart = new Date(start)
				const rangeEnd = new Date(end)
				return eventStart >= rangeStart && eventStart <= rangeEnd
			})
		}
	})

	// Actions
	async function fetchEvents(start?: string, end?: string, force = false) {
		// Return cached data if available, fresh, AND same date-range
		const rangeChanged = start !== lastFetchStart.value || end !== lastFetchEnd.value
		if (!force && !rangeChanged && lastFetch.value && Date.now() - lastFetch.value < CACHE_DURATION) {
			return events.value
		}

		loading.value = true
		error.value = null

		try {
			const params: { start?: string; end?: string; page_size?: number } = { page_size: 500 }
			if (start) params.start = start
			if (end) params.end = end

			const data = await calendarAPI.list(params)
			events.value = data
			lastFetch.value = Date.now()
			lastFetchStart.value = start
			lastFetchEnd.value = end
			return data
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to fetch calendar events')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function fetchEventById(id: number) {
		loading.value = true
		error.value = null

		try {
			const data = await calendarAPI.get(id)
			currentEvent.value = data
			return data
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to fetch calendar event')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function createEvent(eventData: Omit<CalendarEvent, 'id'>) {
		loading.value = true
		error.value = null

		try {
			const data = await calendarAPI.create(eventData)
			events.value = [...events.value, data]
			clearCache()
			return data
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to create calendar event')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function updateEvent(id: number, eventData: Partial<CalendarEvent>) {
		loading.value = true
		error.value = null

		try {
			const data = await calendarAPI.update(id, eventData)
			const index = events.value.findIndex((event) => event.id === id)
			if (index !== -1) {
				const updated = [...events.value]
				updated[index] = data
				events.value = updated
			}
			if (currentEvent.value?.id === id) {
				currentEvent.value = data
			}
			clearCache()
			return data
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to update calendar event')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function deleteEvent(id: number) {
		loading.value = true
		error.value = null

		try {
			await calendarAPI.delete(id)
			events.value = events.value.filter((event) => event.id !== id)
			if (currentEvent.value?.id === id) {
				currentEvent.value = null
			}
			clearCache()
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to delete calendar event')
			throw err
		} finally {
			loading.value = false
		}
	}

	function setView(viewType: CalendarView['currentView']) {
		view.value.currentView = viewType
	}

	function setDate(date: string) {
		view.value.currentDate = date
	}

	function clearCache() {
		lastFetch.value = null
	}

	function reset() {
		events.value = []
		currentEvent.value = null
		error.value = null
		lastFetch.value = null
	}

	return {
		// State
		events,
		currentEvent,
		loading,
		error,
		view,

		// Computed
		upcomingEvents,
		todayEvents,
		getEventById,
		getEventsByEmployee,
		getEventsByProject,
		getEventsByDateRange,

		// Actions
		fetchEvents,
		fetchEventById,
		createEvent,
		updateEvent,
		deleteEvent,
		setView,
		setDate,
		clearCache,
		reset,
	}
})
