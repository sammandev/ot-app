/**
 * SMB Configuration API (Super Admin)
 */

import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface SMBConfigData {
	id?: number
	name: string
	server: string
	share_name: string
	username: string
	new_password?: string
	domain: string
	port: number
	path_prefix: string
	is_active: boolean
	has_password?: boolean
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const smbConfigAPI = {
	async list() {
		const response = await apiClient.get<{
			results: SMBConfigData[]
			count: number
		}>('/v1/smb-configs/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<SMBConfigData>(`/v1/smb-configs/${id}/`)
		return response.data
	},

	async create(data: Partial<SMBConfigData>) {
		const response = await apiClient.post<SMBConfigData>('/v1/smb-configs/', data)
		return response.data
	},

	async update(id: number, data: Partial<SMBConfigData>) {
		const response = await apiClient.patch<SMBConfigData>(`/v1/smb-configs/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/smb-configs/${id}/`)
	},

	async activate(id: number) {
		const response = await apiClient.post<SMBConfigData>(`/v1/smb-configs/${id}/activate/`)
		return response.data
	},

	async testConnection(id: number) {
		const response = await apiClient.post(`/v1/smb-configs/${id}/test/`)
		return response.data
	},
}
