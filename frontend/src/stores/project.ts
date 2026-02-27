/**
 * Project Store
 * Manages project data and API calls
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { PaginatedResponse } from '@/services/api/client'
import { type Project, projectAPI } from '@/services/api/project'

export const useProjectStore = defineStore('project', () => {
	// State
	const projects = ref<Project[]>([])
	const currentProject = ref<Project | null>(null)
	const loading = ref(false)
	const error = ref<string | null>(null)
	const totalCount = ref(0)
	const currentPage = ref(1)
	const pageSize = ref(30)

	// Cache timestamp
	const lastFetched = ref<number | null>(null)
	const CACHE_DURATION = 2 * 60 * 1000 // 2 minutes — projects rarely change

	// Computed
	const enabledProjects = computed(() => projects.value.filter((p) => p.is_enabled))

	const getProjectById = computed(() => {
		return (id: number) => projects.value.find((p) => p.id === id)
	})

	const getProjectByName = computed(() => {
		return (name: string) => projects.value.find((p) => p.name === name)
	})

	const isCacheValid = computed(() => {
		if (!lastFetched.value) return false
		return Date.now() - lastFetched.value < CACHE_DURATION
	})

	// Actions
	const fetchProjects = async (params?: { page?: number; page_size?: number; search?: string }) => {
		// Use cache if valid and no specific params
		if (!params && isCacheValid.value && projects.value.length > 0) {
			return projects.value
		}

		loading.value = true
		error.value = null

		try {
			// Fetch projects with a reasonable default page size
			const fetchParams = params || { page_size: 200 }
			const response: PaginatedResponse<Project> = await projectAPI.list(fetchParams)
			projects.value = response.results
			totalCount.value = response.count
			currentPage.value = fetchParams.page || 1
			pageSize.value = fetchParams.page_size || 30
			lastFetched.value = Date.now()
			return response.results
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to fetch projects'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const fetchProjectById = async (id: number) => {
		loading.value = true
		error.value = null

		try {
			const project = await projectAPI.get(id)
			currentProject.value = project

			// Update in list if exists
			const index = projects.value.findIndex((p) => p.id === id)
			if (index > -1) {
				projects.value[index] = project
			}

			return project
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to fetch project'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const createProject = async (payload: { name: string; is_enabled?: boolean }) => {
		loading.value = true
		error.value = null

		try {
			const project = await projectAPI.create(payload)
			projects.value.unshift(project)
			totalCount.value += 1
			return project
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to create project'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const updateProject = async (id: number, payload: { name?: string; is_enabled?: boolean }) => {
		loading.value = true
		error.value = null

		try {
			const project = await projectAPI.update(id, payload)

			// Update in list
			const index = projects.value.findIndex((p) => p.id === id)
			if (index > -1) {
				projects.value[index] = project
			}

			if (currentProject.value?.id === id) {
				currentProject.value = project
			}

			return project
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to update project'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const deleteProject = async (id: number) => {
		loading.value = true
		error.value = null

		try {
			await projectAPI.delete(id)

			// Remove from list
			const index = projects.value.findIndex((p) => p.id === id)
			if (index > -1) {
				projects.value.splice(index, 1)
				totalCount.value -= 1
			}

			if (currentProject.value?.id === id) {
				currentProject.value = null
			}
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to delete project'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const setEnabled = async (id: number, enabled: boolean) => {
		loading.value = true
		error.value = null

		try {
			const project = await projectAPI.update(id, { is_enabled: enabled })

			// Update in list
			const index = projects.value.findIndex((p) => p.id === id)
			if (index > -1) {
				projects.value[index] = project
			}

			return project
		} catch (err: unknown) {
			const errorMessage = err instanceof Error ? err.message : 'Failed to update project status'
			error.value = errorMessage
			throw err
		} finally {
			loading.value = false
		}
	}

	const clearCache = () => {
		lastFetched.value = null
	}

	const reset = () => {
		projects.value = []
		currentProject.value = null
		loading.value = false
		error.value = null
		totalCount.value = 0
		currentPage.value = 1
		lastFetched.value = null
	}

	return {
		// State
		projects,
		currentProject,
		loading,
		error,
		totalCount,
		currentPage,
		pageSize,

		// Computed
		enabledProjects,
		getProjectById,
		getProjectByName,
		isCacheValid,

		// Actions
		fetchProjects,
		fetchProjectById,
		createProject,
		updateProject,
		deleteProject,
		setEnabled,
		clearCache,
		reset,
	}
})
