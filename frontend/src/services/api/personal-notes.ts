/**
 * Personal Notes API — Kanban personal sticky notes board
 */

import { apiClient } from './client'

// ============================================================================
// Types
// ============================================================================

export interface PersonalNote {
	id: number
	owner: number
	owner_username?: string
	title: string
	content?: string
	color: string // Hex color code (default: #FFEB3B)
	is_pinned: boolean
	is_completed: boolean
	due_date?: string // YYYY-MM-DD
	order: number
	created_at?: string
	updated_at?: string
}

// ============================================================================
// API Endpoints
// ============================================================================

export const personalNoteAPI = {
	async list() {
		const response = await apiClient.get<PersonalNote[]>('/v1/personal-notes/')
		return response.data
	},

	async get(id: number) {
		const response = await apiClient.get<PersonalNote>(`/v1/personal-notes/${id}/`)
		return response.data
	},

	async create(payload: { title: string; content?: string; color?: string; due_date?: string }) {
		const response = await apiClient.post<PersonalNote>('/v1/personal-notes/', payload)
		return response.data
	},

	async update(id: number, payload: Partial<PersonalNote>) {
		const response = await apiClient.patch<PersonalNote>(`/v1/personal-notes/${id}/`, payload)
		return response.data
	},

	async delete(id: number) {
		await apiClient.delete(`/v1/personal-notes/${id}/`)
	},

	async reorder(order: number[]) {
		const response = await apiClient.post<{ status: string }>('/v1/personal-notes/reorder/', {
			order,
		})
		return response.data
	},

	async togglePin(id: number) {
		const response = await apiClient.post<PersonalNote>(`/v1/personal-notes/${id}/toggle_pin/`)
		return response.data
	},

	async toggleComplete(id: number) {
		const response = await apiClient.post<PersonalNote>(`/v1/personal-notes/${id}/toggle_complete/`)
		return response.data
	},
}
