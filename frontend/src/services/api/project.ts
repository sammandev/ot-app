/**
 * Project API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface Project {
	id: number
	name: string
	is_enabled: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const projectAPI = {
	async list(params?: { page?: number; page_size?: number; search?: string }) {
		const response = await apiClient.get<PaginatedResponse<Project>>('/v1/projects/', {
			params,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Project>(`/v1/projects/${id}/`)
		return response.data
	},

	async create(payload: { name: string; is_enabled?: boolean }) {
		const response = await apiClient.post<Project>('/v1/projects/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<{ name: string; is_enabled: boolean }>) {
		const response = await apiClient.patch<Project>(`/v1/projects/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/projects/${id}/`)
	},
}
