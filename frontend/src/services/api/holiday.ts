/**
 * Holiday & Employee Leave API
 */

import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface Holiday {
	id: number
	title: string
	date: string // YYYY-MM-DD
	color: string // Hex color code
	description?: string
	is_recurring: boolean
	created_by?: number
	created_by_username?: string
	created_at?: string
	updated_at?: string
}

export interface EmployeeLeave {
	id: number
	employee: number
	employee_name: string
	employee_emp_id: string
	employee_dept_code?: string | null
	date: string // YYYY-MM-DD
	notes?: string
	agents?: number[] // Array of agent employee IDs
	agent_ids?: number[] // Read-only list of agent IDs
	agent_details?: Array<{
		id: number
		name: string
		emp_id: string
		dept_code?: string | null
	}> // Read-only agent details
	agent_names?: string // Custom agent names (free text)
	created_by?: number
	created_by_username?: string
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const holidayAPI = {
	async list(
		params?: { year?: number; month?: number; start_date?: string; end_date?: string },
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<Holiday[]>('/v1/holidays/', {
			params,
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Holiday>(`/v1/holidays/${id}/`)
		return response.data
	},

	async create(
		payload: Omit<Holiday, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'created_by_username'>,
	) {
		const response = await apiClient.post<Holiday>('/v1/holidays/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<Holiday>) {
		const response = await apiClient.patch<Holiday>(`/v1/holidays/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/holidays/${id}/`)
	},
}

export const employeeLeaveAPI = {
	async list(
		params?: {
			year?: number
			month?: number
			start_date?: string
			end_date?: string
			employee?: number
			date?: string
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<EmployeeLeave[]>('/v1/employee-leaves/', {
			params,
			signal: requestOptions?.signal,
		})
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<EmployeeLeave>(`/v1/employee-leaves/${id}/`)
		return response.data
	},

	async create(payload: {
		employee: number
		date: string
		notes?: string
		agents?: number[]
		agent_names?: string
	}) {
		const response = await apiClient.post<EmployeeLeave>('/v1/employee-leaves/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<EmployeeLeave>) {
		const response = await apiClient.patch<EmployeeLeave>(`/v1/employee-leaves/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/employee-leaves/${id}/`)
	},
}
