import type { PaginatedResponse } from './client'
import { apiClient } from './client'

export type DocumentSourceType = 'file' | 'link'
export type DocumentPreviewType = 'image' | 'pdf' | 'text' | 'csv' | null

export interface DocumentSummary {
	id: number
	title: string
	source_type: DocumentSourceType
	category: string
	tags: string[]
	is_pinned: boolean
	original_filename: string
	stored_file_size: number | null
	mime_type: string
	extension: string
	created_by: number | null
	created_by_name: string | null
	created_at: string
	updated_at: string
	file_url: string | null
	external_url: string
	host: string
	can_preview: boolean
	preview_type: DocumentPreviewType
	is_external: boolean
	link_site_name: string
	metadata_status: 'pending' | 'success' | 'failed'
	metadata_fetched_at: string | null
}

export interface DocumentDetail extends DocumentSummary {
	description: string
	normalized_url: string
	updated_by: number | null
	link_title: string
	link_description: string
	link_favicon_url: string
	link_image_url: string
	metadata_error: string
}

export interface DocumentWritePayload {
	title?: string
	description?: string
	source_type: DocumentSourceType
	file?: File | null
	external_url?: string
	category?: string
	tags?: string[]
	is_pinned?: boolean
}

export interface DocumentFilterOptions {
	categories: string[]
	tags: string[]
}

function buildMultipartPayload(data: DocumentWritePayload) {
	const formData = new FormData()
	formData.append('source_type', data.source_type)
	if (data.title) formData.append('title', data.title)
	if (data.description) formData.append('description', data.description)
	if (data.category) formData.append('category', data.category)
	if (typeof data.is_pinned === 'boolean') formData.append('is_pinned', String(data.is_pinned))
	if (data.tags) formData.append('tags', JSON.stringify(data.tags))
	if (data.external_url) formData.append('external_url', data.external_url)
	if (data.file) formData.append('file', data.file)
	return formData
}

export const documentAPI = {
	async list(params?: {
		page?: number
		page_size?: number
		search?: string
		categories?: string[]
		tags?: string[]
		source_type?: DocumentSourceType | ''
		pinned?: boolean
		ordering?: string
	}) {
		const normalizedParams = {
			...params,
			categories: params?.categories?.join(',') || undefined,
			tags: params?.tags?.join(',') || undefined,
		}
		const response = await apiClient.get<PaginatedResponse<DocumentSummary>>('/v1/documents/', {
			params: normalizedParams,
		})
		return response.data
	},

	async getFilterOptions() {
		const response = await apiClient.get<DocumentFilterOptions>('/v1/documents/filter-options/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<DocumentDetail>(`/v1/documents/${id}/`)
		return response.data
	},

	async create(data: DocumentWritePayload) {
		if (data.file) {
			const response = await apiClient.post<DocumentDetail>('/v1/documents/', buildMultipartPayload(data), {
				headers: { 'Content-Type': 'multipart/form-data' },
			})
			return response.data
		}

		const response = await apiClient.post<DocumentDetail>('/v1/documents/', data)
		return response.data
	},

	async update(id: number, data: DocumentWritePayload) {
		if (data.file) {
			const response = await apiClient.patch<DocumentDetail>(`/v1/documents/${id}/`, buildMultipartPayload(data), {
				headers: { 'Content-Type': 'multipart/form-data' },
			})
			return response.data
		}

		const response = await apiClient.patch<DocumentDetail>(`/v1/documents/${id}/`, data)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/documents/${id}/`)
	},

	async bulkPin(ids: number[], pinned: boolean) {
		const response = await apiClient.post<{ count: number; pinned: boolean }>('/v1/documents/bulk-pin/', {
			ids,
			pinned,
		})
		return response.data
	},

	async bulkDelete(ids: number[]) {
		const response = await apiClient.post<{ count: number }>('/v1/documents/bulk-delete/', { ids })
		return response.data
	},

	async loadPreviewContent(fileUrl: string) {
		const response = await apiClient.get<string>(fileUrl, {
			responseType: 'text',
			transformResponse: [(data) => data],
		})
		return response.data
	},

	async refreshMetadata(id: number) {
		const response = await apiClient.post<DocumentDetail>(`/v1/documents/${id}/refresh-metadata/`)
		return response.data
	},
}