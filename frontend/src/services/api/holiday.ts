/**
 * Holiday & Employee Leave API
 */

import type { PaginatedResponse } from './client'
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

export interface ExternalLookupLeaveAgent {
	username: string
	email: string
	worker_id: string
	site?: string | null
	source?: 'external_lookup'
}

export interface EmployeeLeaveAgent {
	type: 'employee'
	employee_id: number
	name: string
	emp_id: string
	dept_code?: string | null
}

export interface ExternalLeaveAgent extends ExternalLookupLeaveAgent {
	type: 'external'
}

export interface ManualLeaveAgent {
	type: 'manual'
	name: string
}

export type LeaveAgent = EmployeeLeaveAgent | ExternalLeaveAgent | ManualLeaveAgent

export interface EmployeeLeave {
	id: number
	employee: number
	employee_name: string
	employee_emp_id: string
	employee_dept_code?: string | null
	date: string // YYYY-MM-DD
	batch_key?: string | null
	notes?: string
	agents?: LeaveAgent[]
	agent_ids?: number[] // Read-only list of agent IDs
	agent_details?: Array<{
		id: number
		name: string
		emp_id: string
		dept_code?: string | null
	}> // Read-only agent details
	created_by?: number
	created_by_username?: string
	created_at?: string
	updated_at?: string
}

export interface EmployeeLeaveBatchCreatePayload {
	employee: number
	dates: string[]
	notes?: string
	agents?: LeaveAgent[]
}

export interface EmployeeLeaveBatchUpdatePayload extends EmployeeLeaveBatchCreatePayload {
	leave_ids: number[]
}

export interface EmployeeLeavePreview {
	batch_key: string
	employee_name: string
	employee_id: string
	employee_email: string
	department_name: string
	department_code: string
	dates: string[]
	leave_day_count: number
	agents: string[]
	note: string
	submitted_by: string
	created_at_label?: string
	updated_at_label?: string
	created_at?: string
	updated_at?: string
}

export interface ExternalLeaveAgentLookupResponse {
	count: number
	results: ExternalLookupLeaveAgent[]
}

// ============================================================================
// API Endpoints
// ============================================================================

export const holidayAPI = {
	async list(
		params?: { year?: number; month?: number; start_date?: string; end_date?: string },
		requestOptions?: { signal?: AbortSignal },
	) {
		const baseParams = {
			...params,
			page_size: 100,
		}
		const response = await apiClient.get<Holiday[] | PaginatedResponse<Holiday>>('/v1/holidays/', {
			params: baseParams,
			signal: requestOptions?.signal,
		})

		const data = response.data
		if (Array.isArray(data)) return data

		const allResults = [...(data.results ?? [])]
		let next = data.next
		let page = 2
		const maxPages = 20

		while (next && page <= maxPages) {
			const pageResponse = await apiClient.get<PaginatedResponse<Holiday>>('/v1/holidays/', {
				params: { ...baseParams, page },
				signal: requestOptions?.signal,
			})
			allResults.push(...(pageResponse.data.results ?? []))
			next = pageResponse.data.next
			page += 1
		}

		return allResults
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
			batch_key?: string
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const baseParams = {
			...params,
			page_size: 100,
		}
		const response = await apiClient.get<EmployeeLeave[] | PaginatedResponse<EmployeeLeave>>('/v1/employee-leaves/', {
			params: baseParams,
			signal: requestOptions?.signal,
		})

		const data = response.data
		if (Array.isArray(data)) return data

		const allResults = [...(data.results ?? [])]
		let next = data.next
		let page = 2
		const maxPages = 20

		while (next && page <= maxPages) {
			const pageResponse = await apiClient.get<PaginatedResponse<EmployeeLeave>>('/v1/employee-leaves/', {
				params: { ...baseParams, page },
				signal: requestOptions?.signal,
			})
			allResults.push(...(pageResponse.data.results ?? []))
			next = pageResponse.data.next
			page += 1
		}

		return allResults
	},

	async get(id: number) {
		const response = await apiClient.get<EmployeeLeave>(`/v1/employee-leaves/${id}/`)
		return response.data
	},

	async create(payload: {
		employee: number
		date: string
		notes?: string
		agents?: LeaveAgent[]
	}) {
		const response = await apiClient.post<EmployeeLeave>('/v1/employee-leaves/', payload)
		return response.data
	},

	async createBatch(payload: EmployeeLeaveBatchCreatePayload) {
		const response = await apiClient.post<EmployeeLeave[]>('/v1/employee-leaves/batch/', payload)
		return response.data
	},

	async updateBatch(payload: EmployeeLeaveBatchUpdatePayload) {
		const response = await apiClient.patch<EmployeeLeave[]>('/v1/employee-leaves/batch-update/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<EmployeeLeave>) {
		const response = await apiClient.patch<EmployeeLeave>(`/v1/employee-leaves/${id}/`, payload)
		return response.data
	},

	async lookupAgents(keyword: string, requestOptions?: { signal?: AbortSignal }) {
		const response = await apiClient.get<ExternalLeaveAgentLookupResponse>('/v1/employee-leaves/agent-lookup/', {
			params: { keyword },
			signal: requestOptions?.signal,
		})
		return response.data.results ?? []
	},

	async preview(token: string) {
		const response = await apiClient.get<EmployeeLeavePreview>('/v1/employee-leaves/preview/', {
			params: { token },
		})
		return response.data
	},

	async deleteBatch(payload: { leave_ids: number[] }) {
		const response = await apiClient.post<{ deleted_ids: number[] }>('/v1/employee-leaves/batch-delete/', payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/employee-leaves/${id}/`)
	},
}
