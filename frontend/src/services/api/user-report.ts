/**
 * User Reports API
 */

import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface UserReportData {
	id?: number
	reporter?: number
	reporter_name?: string
	reporter_username?: string
	reporter_worker_id?: string
	reporter_email?: string
	report_type: string
	report_type_display?: string
	title: string
	description: string
	page_url?: string
	priority: string
	priority_display?: string
	status?: string
	status_display?: string
	admin_notes?: string
	resolved_in_version?: string
	created_at?: string
	updated_at?: string
}

export interface UserReportStats {
	total: number
	by_status: Record<string, number>
	by_type: Record<string, number>
}

// ============================================================================
// API Endpoints
// ============================================================================

export const userReportAPI = {
	async list(params?: Record<string, string>) {
		const response = await apiClient.get<{
			results: UserReportData[]
			count: number
		}>('/v1/user-reports/', { params })
		return response.data
	},

	async create(data: Partial<UserReportData>) {
		const response = await apiClient.post<UserReportData>('/v1/user-reports/', data)
		return response.data
	},

	async update(id: number, data: Partial<UserReportData>) {
		const response = await apiClient.patch<UserReportData>(`/v1/user-reports/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/user-reports/${id}/`)
	},

	async stats(): Promise<UserReportStats> {
		const response = await apiClient.get<UserReportStats>('/v1/user-reports/stats/')
		return response.data
	},
}
