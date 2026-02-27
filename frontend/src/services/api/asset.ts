/**
 * Asset API
 */

import type { PaginatedResponse } from './client'
import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface Asset {
	id: number
	asset_id: string
	company_code: string | null
	fixed_asset_id: string | null
	is_fixed_asset: boolean
	is_customs_control: boolean
	part_number: string | null
	group_3: string | null
	product_name: string | null
	spec: string | null
	quantity: number
	receive_date: string | null
	status: string | null
	department: number | null
	department_details?: {
		id: number
		code: string
		name: string
	} | null
	cost_center: string | null
	cost_center_name: string | null
	keeper_dept: string | null
	keeper_dept_name: string | null
	keeper: string | null
	keeper_name: string | null
	group_1: string | null
	group_2: string | null
	storage: string | null
	location_code: string | null
	storage_desc: string | null
	consign: string | null
	vendor: string | null
	pr_no: string | null
	pr_sequence: string | null
	po_no: string | null
	po_sequence: string | null
	dn_no: string | null
	dn_sequence: string | null
	dn_date: string | null
	application_number: string | null
	sequence: string | null
	import_number: string | null
	picking_no: string | null
	picking_sequence: string | null
	picking_year: string | null
	picking_date: string | null
	chinese_product_name: string | null
	hs_code: string | null
	declaration_number: string | null
	declaration_date: string | null
	control_end_date: string | null
	outsource_number: string | null
	price: number | null
	currency: string | null
	local_price: number | null
	price_level: string | null
	sn: string | null
	is_qualified: boolean
	itc_end_date: string | null
	elec_declaration_number: string | null
	national_inspection_certification: string | null
	notes: Record<string, string | null>
	created_at: string
	updated_at: string
}

export interface AssetSummary {
	id: number
	asset_id: string
	part_number: string | null
	product_name: string | null
	spec: string | null
	quantity: number
	status: string | null
	cost_center: string | null
	keeper_name: string | null
	keeper_dept: string | null
	department: number | null
	department_code: string | null
	receive_date: string | null
}

export interface DepartmentAssets {
	department_id: number | null
	department_code: string
	department_name: string
	asset_count: number
	assets: AssetSummary[]
}

// ============================================================================
// API Endpoints
// ============================================================================

export const assetAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		department?: number
		cost_center?: string
		status?: string
		ordering?: string
	}) {
		const response = await apiClient.get<PaginatedResponse<AssetSummary>>('/v1/assets/', { params })
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<Asset>(`/v1/assets/${id}/`)
		return response.data
	},

	async create(data: Partial<Asset>) {
		const response = await apiClient.post<Asset>('/v1/assets/', data)
		return response.data
	},

	async update(id: number, data: Partial<Asset>) {
		const response = await apiClient.patch<Asset>(`/v1/assets/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/assets/${id}/`)
	},

	async bulkDelete(ids: number[]) {
		const response = await apiClient.post<{ message: string; deleted: number }>(
			'/v1/assets/bulk_delete/',
			{ ids },
		)
		return response.data
	},

	async bulkUpdateStatus(ids: number[], status: string) {
		const response = await apiClient.post<{ message: string; updated: number }>(
			'/v1/assets/bulk_update_status/',
			{ ids, status },
		)
		return response.data
	},

	async byDepartment(params?: { search?: string }) {
		const response = await apiClient.get<DepartmentAssets[]>('/v1/assets/by_department/', {
			params,
		})
		return response.data
	},

	async importData(file: File) {
		const formData = new FormData()
		formData.append('file', file)
		const response = await apiClient.post<{
			message: string
			created?: number
			updated?: number
		}>('/v1/assets/import_data/', formData, {
			headers: { 'Content-Type': 'multipart/form-data' },
		})
		return response.data
	},
}
