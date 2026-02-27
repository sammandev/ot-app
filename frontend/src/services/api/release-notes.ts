/**
 * Release Notes API
 */

import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface ReleaseNoteData {
	id?: number
	version: string
	release_date: string
	status: string
	status_display?: string
	summary: string
	new_features: string[]
	improvements: string[]
	bug_fixes: string[]
	breaking_changes: string[]
	security: string[]
	known_issues: string[]
	deprecations: string[]
	contributors: string[]
	published: boolean
	created_by?: number
	created_by_name?: string
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const releaseNoteAPI = {
	async list() {
		const response = await apiClient.get<{
			results: ReleaseNoteData[]
			count: number
		}>('/v1/release-notes/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<ReleaseNoteData>(`/v1/release-notes/${id}/`)
		return response.data
	},

	async create(data: Partial<ReleaseNoteData>) {
		const response = await apiClient.post<ReleaseNoteData>('/v1/release-notes/', data)
		return response.data
	},

	async update(id: number, data: Partial<ReleaseNoteData>) {
		const response = await apiClient.patch<ReleaseNoteData>(`/v1/release-notes/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/release-notes/${id}/`)
	},
}
