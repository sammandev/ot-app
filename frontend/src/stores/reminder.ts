import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { type CalendarEvent, calendarAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useConfigStore } from '@/stores/config'

export interface ReminderItem {
	id: string
	eventId: number
	title: string
	message: string
	type: 'meeting' | 'task' | 'due_date' | 'event'
	eventTime: Date
	dismissed: boolean
	snoozedUntil: Date | null
}

export const useReminderStore = defineStore('reminder', () => {
	const reminders = ref<ReminderItem[]>([])
	const dismissedEventIds = ref<Set<number>>(new Set())
	const snoozeSettings = ref<Map<number, number>>(new Map()) // eventId -> interval in minutes
	const pollingInterval = ref<ReturnType<typeof setInterval> | null>(null)

	const activeReminders = computed(() =>
		reminders.value.filter((r) => {
			if (r.dismissed) return false
			if (r.snoozedUntil && new Date() < r.snoozedUntil) return false
			return true
		}),
	)

	const loadDismissedFromStorage = () => {
		try {
			const stored = localStorage.getItem('dismissed_reminders')
			if (stored) {
				const ids = JSON.parse(stored) as number[]
				dismissedEventIds.value = new Set(ids)
			}
			const snoozeStored = localStorage.getItem('snooze_settings')
			if (snoozeStored) {
				const settings = JSON.parse(snoozeStored) as [number, number][]
				snoozeSettings.value = new Map(settings)
			}
		} catch (e) {
			console.error('Failed to load dismissed reminders', e)
		}
	}

	const saveDismissedToStorage = () => {
		try {
			localStorage.setItem('dismissed_reminders', JSON.stringify([...dismissedEventIds.value]))
			localStorage.setItem('snooze_settings', JSON.stringify([...snoozeSettings.value.entries()]))
		} catch (e) {
			console.error('Failed to save dismissed reminders', e)
		}
	}

	const clearOldDismissedEvents = () => {
		// Clear dismissed events that are more than 24 hours old
		// This is a simple cleanup - in production you might want more sophisticated logic
		const today = new Date()
		today.setHours(0, 0, 0, 0)
		const todayStr = today.toISOString().split('T')[0]
		const storedDate = localStorage.getItem('dismissed_reminders_date')

		if (storedDate !== todayStr) {
			dismissedEventIds.value.clear()
			snoozeSettings.value.clear()
			localStorage.setItem('dismissed_reminders_date', todayStr!)
			saveDismissedToStorage()
		}
	}

	// Hoist store references outside polling loop to avoid repeated store lookups
	let _authStore: ReturnType<typeof useAuthStore> | null = null
	let _configStore: ReturnType<typeof useConfigStore> | null = null
	const getAuthStore = () => {
		if (!_authStore) _authStore = useAuthStore()
		return _authStore
	}
	const getConfigStore = () => {
		if (!_configStore) _configStore = useConfigStore()
		return _configStore
	}

	const checkTodayEvents = async () => {
		try {
			// Check if user is authenticated before making API call
			const authStore = getAuthStore()
			if (!authStore.isAuthenticated) {
				return // Don't fetch if not logged in
			}

			// Check if reminders are enabled for this user
			if (authStore.user?.event_reminders_enabled === false) {
				return
			}

			// Check global/role/user disable from system config
			const configStore = getConfigStore()
			if (configStore.eventRemindersDisabledGlobally) {
				return
			}
			// Check if user's role is disabled
			const user = authStore.user
			if (user && configStore.eventRemindersDisabledRoles.length > 0) {
				const userRole = authStore.isDeveloper
					? 'developer'
					: authStore.isSuperAdmin
						? 'superadmin'
						: user.is_superuser
							? 'superuser'
							: authStore.isPtbAdmin
								? 'ptb_admin'
								: user.is_staff
									? 'staff'
									: 'regular'
				if (configStore.eventRemindersDisabledRoles.includes(userRole)) {
					return
				}
			}
			// Check if specific user is disabled
			if (user && configStore.eventRemindersDisabledUsers.includes(user.id)) {
				return
			}

			// Fetch only events relevant to the current user for today and tomorrow
			// (limits the payload instead of fetching the entire event history)
			const todayISO = new Date().toISOString().split('T')[0]
			const tomorrow = new Date()
			tomorrow.setDate(tomorrow.getDate() + 1)
			const tomorrowISO = tomorrow.toISOString().split('T')[0]

			const events = (await calendarAPI.list({
				my_events: true,
				start: todayISO,
				end: tomorrowISO,
			})) as CalendarEvent[]
			const today = new Date()
			const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate())
			const todayEnd = new Date(todayStart)
			todayEnd.setDate(todayEnd.getDate() + 1)

			const newReminders: ReminderItem[] = []

			events.forEach((event) => {
				// Skip if already dismissed
				if (dismissedEventIds.value.has(event.id!)) return

				const eventStart = new Date(event.start)
				const eventEnd = event.end ? new Date(event.end) : eventStart
				const now = new Date()

				// Check if event is happening today
				const isToday = eventStart >= todayStart && eventStart < todayEnd

				// Check if event is within 1 hour (60 minutes)
				const minutesUntilStart = (eventStart.getTime() - now.getTime()) / (1000 * 60)
				const isWithinOneHour = minutesUntilStart > 0 && minutesUntilStart <= 60

				// Check for due date tasks (tasks with status not 'done' and end date is today or passed)
				const isDueToday =
					event.event_type === 'task' &&
					event.status !== 'done' &&
					eventEnd >= todayStart &&
					eventEnd < todayEnd

				const isPastDue =
					event.event_type === 'task' && event.status !== 'done' && eventEnd < todayStart

				// Only show reminders for events within 1 hour, or overdue/due today tasks
				if ((isToday && isWithinOneHour) || isDueToday || isPastDue) {
					const type =
						event.event_type === 'meeting'
							? 'meeting'
							: event.event_type === 'task'
								? isDueToday || isPastDue
									? 'due_date'
									: 'task'
								: 'event'

					let message = ''
					if (type === 'meeting') {
						message = `Meeting "${event.title}" is scheduled for ${eventStart.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`
					} else if (type === 'due_date') {
						message = isPastDue
							? `Task "${event.title}" is overdue!`
							: `Task "${event.title}" is due today at ${eventEnd.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`
					} else if (type === 'task') {
						message = `Task "${event.title}" is scheduled for today`
					} else {
						message = `Event "${event.title}" is happening today at ${eventStart.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}`
					}

					// Check if already in reminders
					const existingIdx = reminders.value.findIndex((r) => r.eventId === event.id!)
					if (existingIdx === -1) {
						newReminders.push({
							id: `reminder-${event.id}-${Date.now()}`,
							eventId: event.id!,
							title: event.title,
							message,
							type,
							eventTime: eventStart,
							dismissed: false,
							snoozedUntil: null,
						})
					}
				}
			})

			// Add new reminders
			if (newReminders.length > 0) {
				reminders.value.push(...newReminders)
			}
		} catch (e) {
			console.error('Failed to check today events', e)
		}
	}

	const dismissReminder = (eventId: number) => {
		dismissedEventIds.value.add(eventId)
		reminders.value = reminders.value.map((r) =>
			r.eventId === eventId ? { ...r, dismissed: true } : r,
		)
		snoozeSettings.value.delete(eventId)
		saveDismissedToStorage()
	}

	const snoozeReminder = (eventId: number, minutes: number) => {
		const snoozeUntil = new Date()
		snoozeUntil.setMinutes(snoozeUntil.getMinutes() + minutes)

		reminders.value = reminders.value.map((r) =>
			r.eventId === eventId ? { ...r, snoozedUntil: snoozeUntil } : r,
		)
		snoozeSettings.value.set(eventId, minutes)
		saveDismissedToStorage()
	}

	const getSnoozeInterval = (eventId: number) => {
		return snoozeSettings.value.get(eventId) || 15
	}

	const startPolling = async (intervalMinutes = 5) => {
		// Bail out immediately if user is not authenticated
		const authStore = getAuthStore()
		if (!authStore.isAuthenticated) {
			return
		}

		loadDismissedFromStorage()
		clearOldDismissedEvents()

		// Ensure config is loaded before first check so disable settings are respected
		const configStore = getConfigStore()
		if (
			!configStore.eventRemindersDisabledGlobally &&
			configStore.eventRemindersDisabledRoles.length === 0
		) {
			// Config may not be loaded yet — fetch it (no-op if already loaded)
			try {
				await configStore.fetchConfig()
			} catch {
				/* silent */
			}
		}

		await checkTodayEvents()

		if (pollingInterval.value) {
			clearInterval(pollingInterval.value)
		}

		pollingInterval.value = setInterval(
			() => {
				checkTodayEvents()
			},
			intervalMinutes * 60 * 1000,
		)
	}

	const stopPolling = () => {
		if (pollingInterval.value) {
			clearInterval(pollingInterval.value)
			pollingInterval.value = null
		}
	}

	return {
		reminders,
		activeReminders,
		dismissReminder,
		snoozeReminder,
		getSnoozeInterval,
		startPolling,
		stopPolling,
		checkTodayEvents,
	}
})
