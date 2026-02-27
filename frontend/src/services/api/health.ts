/**
 * Health Check API
 */

import { apiClient } from './client'

export const healthAPI = {
	async check() {
		const response = await apiClient.get('/health/')
		return response.data
	},

	async detailed() {
		const response = await apiClient.get('/health/detailed/')
		return response.data
	},
}
