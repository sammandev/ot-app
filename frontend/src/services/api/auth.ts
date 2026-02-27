/**
 * Authentication & User Access API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface LoginResponse {
	user: User
}

export interface User {
	id: number
	username: string
	email: string
	first_name: string
	last_name: string
	is_staff: boolean
	is_superuser: boolean
	is_active?: boolean
	is_ptb_admin?: boolean
	role?: 'developer' | 'superadmin' | 'user'
	worker_id?: string
	employee_id?: number
	department_id?: number
	date_joined?: string
	last_login?: string
	groups?: string[]
	permissions?: Record<string, boolean | string | number>
	menu_permissions?: string[] | Record<string, string[]>
	event_reminders_enabled?: boolean
	preferred_language?: string
	permission_updated_at?: string // Timestamp for force logout detection
}

export interface UserAccessControl {
	id: number
	username: string
	worker_id: string
	email: string
	first_name: string
	last_name: string
	is_ptb_admin: boolean
	is_superuser: boolean
	is_staff: boolean
	is_active: boolean
	role?: 'developer' | 'superadmin' | 'user'
	menu_permissions?: string[] | Record<string, string[]>
	event_reminders_enabled?: boolean
	permission_updated_at?: string // Timestamp for force logout detection
}

export interface UserAccessUpdate {
	is_ptb_admin?: boolean
	is_superuser?: boolean
	is_staff?: boolean
	is_active?: boolean
	role?: 'developer' | 'superadmin' | 'user'
	menu_permissions?: string[] | Record<string, string[]>
	event_reminders_enabled?: boolean
}

// ============================================================================
// API Endpoints
// ============================================================================

/**
 * Authentication API
 */
export const authAPI = {
	async loginLocal(credentials: { username: string; password: string }) {
		const response = await apiClient.post<LoginResponse>('/auth/login/local/', credentials)
		return response.data
	},

	async loginExternal(credentials: { username: string; password: string }) {
		const response = await apiClient.post<LoginResponse>('/auth/login/external/', credentials)
		return response.data
	},

	async refreshToken() {
		await apiClient.post('/auth/token/refresh/')
	},

	async logout() {
		await apiClient.post('/auth/logout/')
	},

	async getCurrentUser() {
		const response = await apiClient.get<User>('/auth/me/')
		return response.data
	},

	async updatePreferences(prefs: {
		event_reminders_enabled?: boolean
		preferred_language?: string
	}) {
		const response = await apiClient.patch('/auth/me/', prefs)
		return response.data
	},

	async verifyToken(token: string) {
		const response = await apiClient.post<{
			valid: boolean
			source: 'local' | 'external' | 'unknown'
			details?: {
				user_id?: number
				username?: string
				exp?: number
				iat?: number
				error?: string
			}
		}>('/auth/token/verify/', { token })
		return response.data
	},

	async exchangeExternalToken(token: string) {
		const response = await apiClient.post<{ user: User }>('/auth/exchange-token/', { token })
		return response.data
	},
}

/**
 * User Access Control API (Super Admin only)
 */
export const userAccessAPI = {
	async getAll() {
		const response = await apiClient.get<PaginatedResponse<UserAccessControl>>(
			'/v1/users/access-control/',
		)
		return response.data.results
	},

	async update(userId: number, data: UserAccessUpdate) {
		const response = await apiClient.patch<UserAccessControl>(
			`/v1/users/access-control/${userId}/`,
			data,
		)
		return response.data
	},
}
