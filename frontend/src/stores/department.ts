/**
 * Department Store
 * Manages department data with caching and CRUD operations
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { PaginatedResponse } from '@/services/api/client'
import { type Department, departmentAPI } from '@/services/api/department'
import { extractApiError } from '@/utils/extractApiError'

export const useDepartmentStore = defineStore('department', () => {
	// State
	const departments = ref<Department[]>([])
	const loading = ref(false)
	const error = ref<string | null>(null)
	const lastFetch = ref<number | null>(null)
	const totalCount = ref(0)

	// Cache duration: 2 minutes — departments rarely change
	const CACHE_DURATION = 2 * 60 * 1000

	// Computed
	const enabledDepartments = computed(() => departments.value.filter((dept) => dept.is_enabled))

	const getDepartmentById = computed(() => {
		return (id: number) => departments.value.find((dept) => dept.id === id)
	})

	const getDepartmentByName = computed(() => {
		return (name: string) => departments.value.find((dept) => dept.name === name)
	})

	// Actions
	async function fetchDepartments(force = false) {
		// Return cached data if available and fresh
		if (!force && lastFetch.value && Date.now() - lastFetch.value < CACHE_DURATION) {
			return departments.value
		}

		loading.value = true
		error.value = null

		try {
			const response: PaginatedResponse<Department> = await departmentAPI.list({
				page_size: 200,
			})
			departments.value = response.results
			totalCount.value = response.count ?? response.results.length
			lastFetch.value = Date.now()
			return response.results
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to fetch departments')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function createDepartment(departmentData: {
		code: string
		name: string
		is_enabled?: boolean
	}) {
		loading.value = true
		error.value = null

		try {
			const data = await departmentAPI.create(departmentData)
			departments.value.push(data)
			return data
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to create department')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function updateDepartment(id: number, departmentData: Partial<Department>) {
		loading.value = true
		error.value = null

		try {
			const data = await departmentAPI.update(id, departmentData)
			const index = departments.value.findIndex((dept) => dept.id === id)
			if (index !== -1) {
				departments.value[index] = data
			}
			return data
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to update department')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function deleteDepartment(id: number) {
		loading.value = true
		error.value = null

		try {
			await departmentAPI.delete(id)
			departments.value = departments.value.filter((dept) => dept.id !== id)
		} catch (err: unknown) {
			error.value = extractApiError(err, 'Failed to delete department')
			throw err
		} finally {
			loading.value = false
		}
	}

	async function setEnabled(id: number, enabled: boolean) {
		return updateDepartment(id, { is_enabled: enabled })
	}

	function clearCache() {
		lastFetch.value = null
	}

	function reset() {
		departments.value = []
		loading.value = false
		error.value = null
		lastFetch.value = null
		totalCount.value = 0
	}

	return {
		// State
		departments,
		loading,
		error,
		totalCount,

		// Computed
		enabledDepartments,
		getDepartmentById,
		getDepartmentByName,

		// Actions
		fetchDepartments,
		createDepartment,
		updateDepartment,
		deleteDepartment,
		setEnabled,
		clearCache,
		reset,
	}
})
