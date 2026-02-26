/**
 * Calendar event types - must match backend EVENT_TYPES
 */

export type CalendarEventType = 'holiday' | 'leave' | 'meeting' | 'task'

export type RepeatFrequency = 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly'

export interface CalendarEventPayload {
	title: string
	event_type: CalendarEventType
	description?: string
	start: string
	end: string
	all_day?: boolean
	created_by?: number | null
	assigned_to?: number[]
	meeting_url?: string
	project?: number | null
	applied_by?: number | null
	agent?: number | null
	leave_type?: string
	is_repeating?: boolean
	repeat_frequency?: RepeatFrequency
}

export interface CalendarEventResponse extends CalendarEventPayload {
	id: number
}

export interface CalendarEventExtendedProps {
	event_type: CalendarEventType
	description?: string
	created_by?: number | null
	assigned_to?: number[]
	meeting_url?: string
	project?: number | null
	applied_by?: number | null
	agent?: number | null
	leave_type?: string
	all_day?: boolean
	is_repeating?: boolean
	repeat_frequency?: RepeatFrequency
	parent_event?: number | null
}

export interface CalendarEventInput {
	id: string
	title?: string
	start: Date | string
	end?: Date | string | null
	allDay?: boolean
	color?: string
	backgroundColor?: string
	display?: 'auto' | 'block' | 'list-item' | 'background' | 'inverse-background' | 'none'
	extendedProps:
		| CalendarEventExtendedProps
		| {
				event_type: string
				title?: string
				description?: string
		  }
}
