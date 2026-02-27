/**
 * Notification API
 */

import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface Notification {
	id: number
	title: string
	message: string
	is_read: boolean
	is_archived?: boolean
	created_at: string
	time_ago: string
	recipient: number
	event: number | null
	event_type?: string // 'meeting', 'task', 'leave', 'holiday', 'purchase_request'
	computed_event_type?: string // Computed event type from linked event
	meeting_url?: string | null // URL for meetings
}

export interface PaginatedNotifications {
	count: number
	next: string | null
	previous: string | null
	total_pages: number
	current_page: number
	results: Notification[]
}

export interface UnreadCountResponse {
	unread_count: number
}

// ============================================================================
// API Endpoints
// ============================================================================

export const notificationAPI = {
	async list(
		params?: {
			page?: number
			limit?: number
			no_pagination?: boolean
			include_archived?: boolean
			archived_only?: boolean
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<PaginatedNotifications | Notification[]>(
			'/v1/notifications/',
			{
				params: {
					page: params?.page,
					limit: params?.limit,
					no_pagination: params?.no_pagination ? 'true' : undefined,
					include_archived: params?.include_archived ? 'true' : undefined,
					archived_only: params?.archived_only ? 'true' : undefined,
				},
				signal: requestOptions?.signal,
			},
		)
		return response.data
	},

	async getLatest(limit: number = 10, requestOptions?: { signal?: AbortSignal }) {
		const response = await apiClient.get<Notification[]>('/v1/notifications/', {
			params: { no_pagination: 'true', limit },
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async getUnreadCount(requestOptions?: { signal?: AbortSignal }) {
		const response = await apiClient.get<UnreadCountResponse>('/v1/notifications/unread-count/', {
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async markRead(id: number) {
		const response = await apiClient.post<{ status: string }>(`/v1/notifications/${id}/mark_read/`)
		return response.data
	},

	async markAllRead() {
		const response = await apiClient.post<{ status: string; count: number }>(
			'/v1/notifications/mark-all-read/',
		)
		return response.data
	},

	async archiveOld(days: number = 90) {
		const response = await apiClient.post<{ status: string; count: number }>(
			'/v1/notifications/archive-old/',
			{ days },
		)
		return response.data
	},

	async archiveNotification(id: number) {
		const response = await apiClient.post<{ status: string }>(`/v1/notifications/${id}/archive/`)
		return response.data
	},

	async unarchiveNotification(id: number) {
		const response = await apiClient.post<{ status: string }>(`/v1/notifications/${id}/unarchive/`)
		return response.data
	},

	async deleteNotification(id: number) {
		await apiClient.delete(`/v1/notifications/${id}/`)
	},
}
