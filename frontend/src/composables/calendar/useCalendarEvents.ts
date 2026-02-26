import { ref } from 'vue'
import { calendarAPI } from '@/services/calendar'
import type {
	CalendarEventInput,
	CalendarEventPayload,
	CalendarEventResponse,
	CalendarEventType,
} from '@/types/calendar'

const getEventType = (eventType?: string): CalendarEventType => {
	if (
		eventType === 'holiday' ||
		eventType === 'leave' ||
		eventType === 'meeting' ||
		eventType === 'task'
	) {
		return eventType
	}
	return 'task'
}

const formatEventFromAPI = (event: CalendarEventResponse): CalendarEventInput => {
	const eventType = getEventType(event.event_type)
	const startDate = event.start ? new Date(event.start) : new Date()
	const endDate = event.end ? new Date(event.end) : null

	return {
		id: String(event.id),
		title: event.title,
		start: startDate,
		end: endDate,
		allDay: event.all_day ?? (eventType === 'holiday' || eventType === 'leave'),
		extendedProps: {
			event_type: eventType,
			description: event.description,
			created_by: event.created_by ?? null,
			assigned_to: event.assigned_to,
			meeting_url: event.meeting_url,
			project: event.project ?? null,
			applied_by: event.applied_by ?? null,
			agent: event.agent ?? null,
			all_day: event.all_day,
		},
	}
}

export const useCalendarEvents = () => {
	const events = ref<CalendarEventInput[]>([])
	const isLoading = ref(false)
	const error = ref<string | null>(null)

	const loadEvents = async () => {
		isLoading.value = true
		error.value = null
		try {
			const data = await calendarAPI.list()
			events.value = data.map(formatEventFromAPI)
		} catch (err) {
			console.error('Error loading calendar events:', err)
			error.value = 'Failed to load events'
			events.value = []
		} finally {
			isLoading.value = false
		}
	}

	const addEvent = async (payload: CalendarEventPayload) => {
		isLoading.value = true
		error.value = null
		try {
			const data = await calendarAPI.create(payload)
			const formatted = formatEventFromAPI(data)
			events.value.push(formatted)
			return formatted
		} catch (err) {
			console.error('Error creating calendar event:', err)
			error.value = 'Failed to create event'
			throw err
		} finally {
			isLoading.value = false
		}
	}

	const updateEvent = async (id: string | number, payload: CalendarEventPayload) => {
		isLoading.value = true
		error.value = null
		try {
			const data = await calendarAPI.update(id, payload)
			const updated = formatEventFromAPI(data)
			const idx = events.value.findIndex((item) => item.id === String(id))
			if (idx !== -1) {
				events.value[idx] = updated
			}
			return updated
		} catch (err) {
			console.error('Error updating calendar event:', err)
			error.value = 'Failed to update event'
			throw err
		} finally {
			isLoading.value = false
		}
	}

	const deleteEvent = async (id: string | number) => {
		isLoading.value = true
		error.value = null
		try {
			await calendarAPI.remove(id)
			events.value = events.value.filter((item) => item.id !== String(id))
		} catch (err) {
			console.error('Error deleting calendar event:', err)
			error.value = 'Failed to delete event'
			throw err
		} finally {
			isLoading.value = false
		}
	}

	return {
		events,
		isLoading,
		error,
		loadEvents,
		addEvent,
		updateEvent,
		deleteEvent,
	}
}
