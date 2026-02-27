/**
 * Calendar Event API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface CalendarEvent {
	id?: number
	title: string
	start: string
	end: string
	all_day: boolean
	event_type: 'holiday' | 'leave' | 'meeting' | 'task'
	status?: 'todo' | 'in_progress' | 'done'
	description?: string
	location?: string
	color?: string
	priority?: 'low' | 'medium' | 'high' | 'urgent'
	labels?: string[]
	is_repeating?: boolean
	repeat_frequency?: 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | null
	parent_event?: number | null
	created_by?: number
	assigned_to?: number[]
	meeting_url?: string
	project?: number | null
	applied_by?: number | null
	agent?: number | null
	leave_type?: string
	employee?: number
	employee_name?: string
	project_name?: string
	overtime_request?: number
	// Task Group fields
	group?: number | null
	group_name?: string
	group_color?: string
	// Subtask progress fields
	subtask_count?: number
	subtask_completed?: number
	// Time tracking fields
	estimated_hours?: number | null
	actual_hours?: number
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const calendarAPI = {
	async list(params?: {
		start?: string
		end?: string
		employee?: number
		project?: number
		event_type?: 'event' | 'task' | 'meeting' | 'leave' | 'holiday'
		my_events?: boolean
		page?: number
		page_size?: number
	}): Promise<CalendarEvent[]> {
		const baseParams = {
			...params,
			page_size: params?.page_size ?? 500,
		}
		const response = await apiClient.get<CalendarEvent[] | PaginatedResponse<CalendarEvent>>(
			'/v1/calendar-events/',
			{ params: baseParams },
		)

		// Normalize: backend may return paginated { results: [...] } or plain array
		const data = response.data
		if (Array.isArray(data)) return data

		const allResults = [...(data.results ?? [])]
		let next = data.next
		let page = (baseParams.page ?? 1) + 1
		const maxPages = 20

		while (next && page <= maxPages) {
			const pageResponse = await apiClient.get<PaginatedResponse<CalendarEvent>>(
				'/v1/calendar-events/',
				{
					params: { ...baseParams, page },
				},
			)
			allResults.push(...(pageResponse.data.results ?? []))
			next = pageResponse.data.next
			page += 1
		}

		return allResults
	},

	async get(id: number) {
		const response = await apiClient.get<CalendarEvent>(`/v1/calendar-events/${id}/`)
		return response.data
	},

	async create(payload: Omit<CalendarEvent, 'id'>) {
		const response = await apiClient.post<CalendarEvent>('/v1/calendar-events/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<CalendarEvent>) {
		const response = await apiClient.patch<CalendarEvent>(`/v1/calendar-events/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/calendar-events/${id}/`)
	},
}
