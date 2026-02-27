/**
 * Department API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface Department {
	id: number
	code: string
	name: string
	is_enabled: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const departmentAPI = {
	async list(params?: { page?: number; page_size?: number; search?: string }) {
		const response = await apiClient.get<PaginatedResponse<Department>>('/v1/departments/', {
			params,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Department>(`/v1/departments/${id}/`)
		return response.data
	},

	async create(payload: { code: string; name: string; is_enabled?: boolean }) {
		const response = await apiClient.post<Department>('/v1/departments/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<{ code: string; name: string; is_enabled: boolean }>) {
		const response = await apiClient.patch<Department>(`/v1/departments/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/departments/${id}/`)
	},

	async getEmployees(departmentId: number) {
		return apiClient.get<{ id: number; emp_id: string; name: string; is_enabled: boolean }[]>(
			`/v1/departments/${departmentId}/employees/`,
		)
	},

	async removeEmployee(departmentId: number, employeeId: number) {
		return apiClient.post(`/v1/departments/${departmentId}/remove_employee/`, {
			employee_id: employeeId,
		})
	},
}
