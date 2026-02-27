/**
 * Employee API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface Employee {
	id: number
	emp_id: string
	name: string
	department: number
	department_name?: string
	is_enabled: boolean
	exclude_from_reports: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const employeeAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		department_id?: number
		ordering?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<Employee>>('/v1/employees/', {
			params,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Employee>(`/v1/employees/${id}/`)
		return response.data
	},

	async create(payload: {
		emp_id: string
		name: string
		department?: number | null
		is_enabled?: boolean
		exclude_from_reports?: boolean
	}) {
		const response = await apiClient.post<Employee>('/v1/employees/', payload)
		return response.data
	},

	async update(
		id: number,
		payload: Partial<{
			emp_id: string
			name: string
			department: number | null
			is_enabled: boolean
			exclude_from_reports: boolean
		}>,
	) {
		const response = await apiClient.patch<Employee>(`/v1/employees/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/employees/${id}/`)
	},

	async export(params?: { fields?: string }) {
		const response = await apiClient.get('/v1/employees/export/', {
			params,
			responseType: 'blob',
		})
		return response.data
	},

	async bulkImport(file: File, updateExisting = false) {
		const formData = new FormData()
		formData.append('file', file)
		formData.append('update_existing', updateExisting.toString())

		const response = await apiClient.post('/v1/employees/bulk_import/', formData, {
			headers: {
				'Content-Type': 'multipart/form-data',
			},
		})
		return response.data
	},
}
