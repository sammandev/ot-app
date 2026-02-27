/**
 * Overtime API — requests, regulations, limits, documents
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface OvertimeBreak {
	id?: number
	start_time: string
	end_time: string
	duration_minutes?: number
}

export interface OvertimeRequest {
	time_start: string
	id?: number
	employee: number
	employee_name?: string
	employee_id?: string
	employee_emp_id?: string
	department_code?: string
	project: number
	project_name?: string
	request_date: string
	time_end: string
	breaks?: OvertimeBreak[]
	reason?: string
	detail?: string
	status?: 'pending' | 'approved' | 'rejected' | 'cancelled'
	rejection_reason?: string
	approver?: number
	approver_name?: string
	approved_at?: string
	total_duration_minutes?: number
	net_duration_minutes?: number
	total_hours?: number
	has_break?: boolean
	break_start?: string | null
	break_end?: string | null
	break_hours?: number | null
	is_weekend?: boolean
	is_holiday?: boolean
	created_at?: string
	updated_at?: string
}

export interface OvertimeRule {
	id: number
	max_hours_per_day: number
	max_hours_per_week: number
	max_hours_per_month: number
	min_break_duration_minutes: number
	max_continuous_hours: number
	effective_from: string
	effective_until?: string | null
	is_active: boolean
	description?: string
	created_at?: string
	updated_at?: string
}

export interface OvertimeRegulationContent {
	id: number
	title: string
	description: string
	category: string
	order: number
	is_active: boolean
	api_version?: string
	created_at?: string
	updated_at?: string
}

export interface OvertimeRegulationDocument {
	id: number
	title: string
	description?: string
	file: string
	file_size: number
	version: number
	is_active: boolean
	uploaded_by?: number
	uploaded_by_name?: string
	created_at: string
	updated_at: string
}

export interface OvertimeLimitConfig {
	id: number
	max_weekly_hours: number
	max_monthly_hours: number
	advised_weekly_hours: number
	advised_monthly_hours: number
	is_active: boolean
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const overtimeAPI = {
	async list(
		params?: {
			page?: number
			page_size?: number
			employee?: number
			project?: number
			status?: string
			start_date?: string
			end_date?: string
			request_date?: string
			ordering?: string
			search?: string
			department_code?: string
		},
		requestOptions?: { signal?: AbortSignal },
	) {
		const response = await apiClient.get<PaginatedResponse<OvertimeRequest>>(
			'/v1/overtime-requests/',
			{
				params,
				signal: requestOptions?.signal,
			},
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<OvertimeRequest>(`/v1/overtime-requests/${id}/`)
		return response.data
	},

	async create(payload: Omit<OvertimeRequest, 'id'>) {
		const response = await apiClient.post<OvertimeRequest>('/v1/overtime-requests/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<OvertimeRequest>) {
		const response = await apiClient.patch<OvertimeRequest>(`/v1/overtime-requests/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/overtime-requests/${id}/`)
	},

	async approve(id: number) {
		const response = await apiClient.post<OvertimeRequest>(`/v1/overtime-requests/${id}/approve/`)
		return response.data
	},

	async reject(id: number, reason: string) {
		const response = await apiClient.post<OvertimeRequest>(`/v1/overtime-requests/${id}/reject/`, {
			rejection_reason: reason,
		})
		return response.data
	},

	async cancel(id: number) {
		const response = await apiClient.post<OvertimeRequest>(`/v1/overtime-requests/${id}/cancel/`)
		return response.data
	},

	async export(params?: {
		employee?: number
		project?: number
		start_date?: string
		end_date?: string
		format?: 'csv' | 'excel'
	}) {
		const response = await apiClient.get('/v1/overtime-requests/export/', {
			params,
			responseType: 'blob',
		})
		return response.data
	},

	async summary(params?: {
		employee?: number
		project?: number
		start_date?: string
		end_date?: string
		group_by?: 'employee' | 'project' | 'date'
	}) {
		const response = await apiClient.get('/v1/overtime-requests/summary/', {
			params,
		})
		return response.data
	},

	async bulkUpdateStatus(ids: number[], status: 'approved' | 'rejected' | 'pending') {
		const response = await apiClient.post<{
			message: string
			updated_count: number
			status: string
		}>('/v1/overtime-requests/bulk-update-status/', { ids, status })
		return response.data
	},

	async employeeStats(params?: {
		start_date?: string
		end_date?: string
		status?: string
		employee?: number
	}) {
		const response = await apiClient.get<
			Array<{
				employee: number
				employee_name: string
				total_hours: string | number
				total_requests: number
				weekday_hours: string | number
				weekend_hours: string | number
				holiday_hours: string | number
				approved_hours: string | number
				pending_hours: string | number
			}>
		>('/v1/overtime-requests/employee_stats/', { params })
		return response.data
	},

	async projectStats(params?: {
		start_date?: string
		end_date?: string
		status?: string
		project?: number
	}) {
		const response = await apiClient.get<
			Array<{
				project: number
				project_name: string
				total_hours: string | number
				total_requests: number
				unique_employees: number
			}>
		>('/v1/overtime-requests/project_stats/', { params })
		return response.data
	},

	async summaryStats(params?: {
		start_date?: string
		end_date?: string
		prev_start_date?: string
		prev_end_date?: string
	}) {
		const response = await apiClient.get<{
			total_hours: string | number | null
			total_requests: number
			unique_employees: number
			unique_projects: number
			weekday_hours: string | number | null
			weekend_hours: string | number | null
			holiday_hours: string | number | null
			approved_hours: string | number | null
			pending_hours: string | number | null
			rejected_hours: string | number | null
			previous?: {
				total_hours: string | number | null
				total_requests: number
				unique_employees: number
				unique_projects: number
				weekday_hours: string | number | null
				weekend_hours: string | number | null
				holiday_hours: string | number | null
				approved_hours: string | number | null
				pending_hours: string | number | null
				rejected_hours: string | number | null
			}
		}>('/v1/overtime-requests/summary_stats/', { params })
		return response.data
	},
}

/**
 * Overtime Regulation API
 */
export const regulationAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		is_active?: boolean
		category?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<OvertimeRegulationContent>>(
			'/v1/overtime-regulations/',
			{
				params,
			},
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<OvertimeRegulationContent>(`/v1/overtime-regulations/${id}/`)
		return response.data
	},

	async create(payload: Partial<OvertimeRegulationContent>) {
		const response = await apiClient.post<OvertimeRegulationContent>(
			'/v1/overtime-regulations/',
			payload,
		)
		return response.data
	},

	async update(id: number, payload: Partial<OvertimeRegulationContent>) {
		const response = await apiClient.patch<OvertimeRegulationContent>(
			`/v1/overtime-regulations/${id}/`,
			payload,
		)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/overtime-regulations/${id}/`)
	},

	async getActive() {
		const response = await apiClient.get<OvertimeRegulationContent>(
			'/v1/overtime-regulations/active/',
		)
		return response.data
	},
}

export const overtimeLimitAPI = {
	async getActive(): Promise<OvertimeLimitConfig> {
		const response = await apiClient.get<OvertimeLimitConfig>('/v1/overtime-limits/active/')
		return response.data
	},
	async updateLimits(payload: Partial<OvertimeLimitConfig>): Promise<OvertimeLimitConfig> {
		const response = await apiClient.patch<OvertimeLimitConfig>(
			'/v1/overtime-limits/update_limits/',
			payload,
		)
		return response.data
	},
}

/**
 * Overtime Regulation Document API
 */
export const regulationDocumentAPI = {
	async list(params?: { is_active?: boolean; page_size?: number }) {
		const response = await apiClient.get<PaginatedResponse<OvertimeRegulationDocument>>(
			'/v1/regulation-documents/',
			{
				params,
			},
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<OvertimeRegulationDocument>(
			`/v1/regulation-documents/${id}/`,
		)
		return response.data
	},

	async upload(formData: FormData) {
		const response = await apiClient.post<OvertimeRegulationDocument>(
			'/v1/regulation-documents/',
			formData,
			{
				headers: {
					'Content-Type': 'multipart/form-data',
				},
			},
		)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/regulation-documents/${id}/`)
	},
}
