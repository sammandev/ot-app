/**
 * Calendar API service
 */

import type { CalendarEventPayload, CalendarEventResponse } from '@/types/calendar'
import apiClient from './api'

const BASE_PATH = '/v1/calendar-events/'

export interface CalendarListParams {
	event_type?: 'event' | 'task' | 'meeting'
	start_date?: string
	end_date?: string
}

export const calendarAPI = {
	async list(params?: CalendarListParams) {
		const response = await apiClient.get<CalendarEventResponse[]>(BASE_PATH, {
			params,
		})
		return response.data
	},
	async create(payload: CalendarEventPayload) {
		const response = await apiClient.post<CalendarEventResponse>(BASE_PATH, payload)
		return response.data
	},
	async update(id: number | string, payload: CalendarEventPayload) {
		const response = await apiClient.put<CalendarEventResponse>(`${BASE_PATH}${id}/`, payload)
		return response.data
	},
	async remove(id: number | string) {
		await apiClient.delete(`${BASE_PATH}${id}/`)
	},
}

export default calendarAPI
