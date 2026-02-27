/**
 * Calendar API service
 */

import type { CalendarEventPayload, CalendarEventResponse } from '@/types/calendar'
import type { PaginatedResponse } from './api/client'
import apiClient from './api/client'

const BASE_PATH = '/v1/calendar-events/'

export interface CalendarListParams {
	event_type?: 'event' | 'task' | 'meeting'
	start?: string
	end?: string
	page?: number
	page_size?: number
}

export const calendarAPI = {
	async list(params?: CalendarListParams) {
		const baseParams = {
			...params,
			page_size: params?.page_size ?? 500,
		}

		const response = await apiClient.get<
			CalendarEventResponse[] | PaginatedResponse<CalendarEventResponse>
		>(BASE_PATH, {
			params: baseParams,
		})

		if (Array.isArray(response.data)) return response.data

		const allResults = [...(response.data.results ?? [])]
		let next = response.data.next
		let page = (baseParams.page ?? 1) + 1
		const maxPages = 20

		while (next && page <= maxPages) {
			const pageResponse = await apiClient.get<PaginatedResponse<CalendarEventResponse>>(BASE_PATH, {
				params: { ...baseParams, page },
			})
			allResults.push(...(pageResponse.data.results ?? []))
			next = pageResponse.data.next
			page += 1
		}

		return allResults
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
