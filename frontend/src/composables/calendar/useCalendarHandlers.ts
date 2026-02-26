import type { EventApi } from '@fullcalendar/core'
import type { CalendarEventPayload } from '@/types/calendar'

// FullCalendar event handler types
interface EventDropArg {
	event: EventApi
	oldEvent: EventApi
	revert: () => void
}

interface EventResizeDoneArg {
	event: EventApi
	revert: () => void
}

const normalizeIdList = (value: unknown): number[] => {
	if (!Array.isArray(value)) return []
	return value
		.map((v) => {
			const n = typeof v === 'string' ? Number(v) : v
			return Number.isFinite(n as number) ? Number(n) : null
		})
		.filter((v): v is number => v !== null)
}

const normalizeId = (value: unknown): number | null => {
	if (value === null || value === undefined || value === '') return null
	const n = typeof value === 'string' ? Number(value) : value
	return Number.isFinite(n as number) ? Number(n) : null
}

const formatEventData = (event: EventApi): CalendarEventPayload => ({
	title: event.title,
	start: event.start ? event.start.toISOString() : '',
	end: event.end ? event.end.toISOString() : event.start ? event.start.toISOString() : '',
	all_day: event.allDay,
	// Default to task to keep payload valid for the backend
	event_type: event.extendedProps?.event_type || 'task',
	description: event.extendedProps?.description,
	created_by: normalizeId(event.extendedProps?.created_by) ?? undefined,
	assigned_to: normalizeIdList(event.extendedProps?.assigned_to),
	meeting_url: event.extendedProps?.meeting_url || undefined,
	project: normalizeId(event.extendedProps?.project) ?? undefined,
	applied_by: normalizeId(event.extendedProps?.applied_by) ?? undefined,
	agent: normalizeId(event.extendedProps?.agent) ?? undefined,
	leave_type: event.extendedProps?.leave_type || undefined,
})

export const useCalendarHandlers = (
	updateEvent: (id: string | number, payload: CalendarEventPayload) => Promise<void>,
) => {
	const handleEventDrop = async (dropInfo: EventDropArg) => {
		try {
			const payload = formatEventData(dropInfo.event)
			await updateEvent(dropInfo.event.id, payload)
		} catch (error) {
			console.error('Error updating event on drop:', error)
			dropInfo.revert()
		}
	}

	const handleEventResize = async (resizeInfo: EventResizeDoneArg) => {
		try {
			const payload = formatEventData(resizeInfo.event)
			await updateEvent(resizeInfo.event.id, payload)
		} catch (error) {
			console.error('Error updating event on resize:', error)
			resizeInfo.revert()
		}
	}

	return {
		handleEventDrop,
		handleEventResize,
	}
}
