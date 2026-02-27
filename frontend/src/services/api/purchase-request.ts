/**
 * Purchase Request API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface PurchaseRequest {
	id: number
	request_date: string | null
	owner: string | null
	owner_employee: number | null
	owner_employee_details?: {
		id: number
		emp_id: string
		name: string
	} | null
	doc_id: string | null
	part_no: string | null
	description_spec: string | null
	material_category: string | null
	purpose_desc: string | null
	qty: number
	plant: string | null
	project_code: string | null
	pr_type: string | null
	mrp_id: string | null
	purch_org: string | null
	sourcer_price: string | null
	pr_no: string | null
	remarks: string | null
	status: 'pending' | 'done' | 'canceled'
	created_at: string
	updated_at: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const purchaseRequestAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		status?: string
		start_date?: string
		end_date?: string
		ordering?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<PurchaseRequest>>(
			'/v1/purchase-requests/',
			{ params },
		)
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<PurchaseRequest>(`/v1/purchase-requests/${id}/`)
		return response.data
	},

	async create(data: Partial<PurchaseRequest>) {
		const response = await apiClient.post<PurchaseRequest>('/v1/purchase-requests/', data)
		return response.data
	},

	async update(id: number, data: Partial<PurchaseRequest>) {
		const response = await apiClient.patch<PurchaseRequest>(`/v1/purchase-requests/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/purchase-requests/${id}/`)
	},

	async bulkDelete(ids: number[]) {
		const response = await apiClient.post<{ message: string; deleted: number }>(
			'/v1/purchase-requests/bulk_delete/',
			{ ids },
		)
		return response.data
	},

	async bulkUpdateStatus(ids: number[], status: string) {
		const response = await apiClient.post<{ message: string; updated: number }>(
			'/v1/purchase-requests/bulk_update_status/',
			{ ids, status },
		)
		return response.data
	},

	async importData(file: File) {
		const formData = new FormData()
		formData.append('file', file)
		const response = await apiClient.post<{
			message: string
			created?: number
			updated?: number
		}>('/v1/purchase-requests/import_data/', formData, {
			headers: { 'Content-Type': 'multipart/form-data' },
		})
		return response.data
	},
}
