/**
 * Overtime Store
 * Manages overtime requests, breaks, and related operations
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { PaginatedResponse } from '@/services/api/client'
import { type OvertimeRequest, overtimeAPI } from '@/services/api/overtime'
import { extractApiError } from '@/utils/extractApiError'

interface OvertimeFilters {
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
}

interface RequestOptions {
	signal?: AbortSignal
}

export const useOvertimeStore = defineStore('overtime', () => {
	// State
	const requests = ref<OvertimeRequest[]>([])
	const currentRequest = ref<OvertimeRequest | null>(null)
	const _loadingCount = ref(0)
	const loading = computed(() => _loadingCount.value > 0)
	const error = ref<string | null>(null)
	const lastFetch = ref<number | null>(null)

	/** Pagination metadata from last fetchRequests() call */
	const paginationMeta = ref<{
		count: number
		next: string | null
		previous: string | null
	}>({
		count: 0,
		next: null,
		previous: null,
	})

	// Cache duration: 30 seconds (balances freshness vs. performance)
	const CACHE_DURATION = 30_000

	// Computed
	const pendingRequests = computed(() => requests.value.filter((req) => req.status === 'pending'))

	/**
	 * Wraps an async action with the shared loading/error pattern:
	 * increments _loadingCount, clears error, runs fn, extracts error on failure.
	 */
	async function withLoading<T>(fn: () => Promise<T>, fallbackError: string): Promise<T> {
		_loadingCount.value++
		error.value = null
		try {
			return await fn()
		} catch (err: unknown) {
			error.value = extractApiError(err, fallbackError)
			throw err
		} finally {
			_loadingCount.value--
		}
	}

	const approvedRequests = computed(() => requests.value.filter((req) => req.status === 'approved'))

	const rejectedRequests = computed(() => requests.value.filter((req) => req.status === 'rejected'))

	const getRequestById = computed(() => {
		return (id: number) => requests.value.find((req) => req.id === id)
	})

	const getRequestsByEmployee = computed(() => {
		return (employeeId: number) => requests.value.filter((req) => req.employee === employeeId)
	})

	const getRequestsByProject = computed(() => {
		return (projectId: number) => requests.value.filter((req) => req.project === projectId)
	})

	// Actions
	async function fetchRequests(
		filters?: OvertimeFilters,
		force = false,
		requestOptions?: RequestOptions,
	) {
		// Return cached data if no filters and cache is fresh
		if (
			!force &&
			CACHE_DURATION > 0 &&
			!filters &&
			lastFetch.value &&
			Date.now() - lastFetch.value < CACHE_DURATION
		) {
			return requests.value
		}

		_loadingCount.value++
		error.value = null

		try {
			// Fetch overtime requests with reasonable page size to avoid huge payloads
			const fetchFilters = filters || { page_size: 200 }
			const response: PaginatedResponse<OvertimeRequest> = await overtimeAPI.list(
				fetchFilters,
				requestOptions,
			)
			requests.value = response.results
			paginationMeta.value = {
				count: response.count ?? response.results.length,
				next: response.next ?? null,
				previous: response.previous ?? null,
			}
			lastFetch.value = Date.now()
			return response
		} catch (err: unknown) {
			const cancelledError =
				typeof err === 'object' &&
				err !== null &&
				('code' in err || 'name' in err) &&
				((err as { code?: string }).code === 'ERR_CANCELED' ||
					(err as { name?: string }).name === 'CanceledError')
			if (cancelledError) {
				throw err
			}

			error.value = extractApiError(err, 'Failed to fetch overtime requests')
			throw err
		} finally {
			_loadingCount.value--
		}
	}

	// AbortController for fetchAllRequests — allows cancellation of multi-page fetch
	let _fetchAllController: AbortController | null = null

	/** Fetch overtime requests with sane defaults to avoid heavy queries. */
	async function fetchAllRequests(filters?: OvertimeFilters, options?: RequestOptions) {
		// Cancel any in-flight fetchAllRequests
		if (_fetchAllController) {
			_fetchAllController.abort()
		}
		_fetchAllController = new AbortController()
		const signal = options?.signal ? options.signal : _fetchAllController.signal

		// Default to last 90 days if no date range provided
		const today = new Date()
		const defaultStart = new Date(today)
		defaultStart.setDate(defaultStart.getDate() - 90)

		const baseFilters: OvertimeFilters = {
			...filters,
			start_date: filters?.start_date || defaultStart.toISOString().slice(0, 10),
			end_date: filters?.end_date || today.toISOString().slice(0, 10),
		}

		const pageSize = Math.min(500, baseFilters.page_size || 500)
		let page = 1
		const all: OvertimeRequest[] = []

		// Prevent runaway pagination
		const MAX_PAGES = 20

		while (page <= MAX_PAGES) {
			signal.throwIfAborted()
			const params: OvertimeFilters = {
				...baseFilters,
				ordering: '-created_at',
				page,
				page_size: pageSize,
			}

			const response: PaginatedResponse<OvertimeRequest> = await overtimeAPI.list(params, { signal })
			all.push(...response.results)

			if (!response.next) break
			page += 1
		}

		// Update store state for consistency with fetchRequests
		requests.value = all
		paginationMeta.value = { count: all.length, next: null, previous: null }
		lastFetch.value = Date.now()

		return all
	}

	async function fetchRequestById(id: number) {
		return withLoading(async () => {
			const data = await overtimeAPI.get(id)
			currentRequest.value = data
			return data
		}, 'Failed to fetch overtime request')
	}

	async function createRequest(requestData: Omit<OvertimeRequest, 'id'>) {
		return withLoading(async () => {
			const data = await overtimeAPI.create(requestData)
			requests.value.unshift(data)
			clearCache()
			return data
		}, 'Failed to create overtime request')
	}

	async function updateRequest(id: number, requestData: Partial<OvertimeRequest>) {
		return withLoading(async () => {
			const data = await overtimeAPI.update(id, requestData)
			const index = requests.value.findIndex((req) => req.id === id)
			if (index !== -1) {
				requests.value[index] = data
			}
			if (currentRequest.value?.id === id) {
				currentRequest.value = data
			}
			clearCache()
			return data
		}, 'Failed to update overtime request')
	}

	async function deleteRequest(id: number) {
		return withLoading(async () => {
			await overtimeAPI.delete(id)
			requests.value = requests.value.filter((req) => req.id !== id)
			if (currentRequest.value?.id === id) {
				currentRequest.value = null
			}
			clearCache()
		}, 'Failed to delete overtime request')
	}

	async function approveRequest(id: number) {
		return withLoading(async () => {
			const data = await overtimeAPI.approve(id)
			const index = requests.value.findIndex((req) => req.id === id)
			if (index !== -1) {
				requests.value[index] = data
			}
			clearCache()
			return data
		}, 'Failed to approve request')
	}

	async function rejectRequest(id: number, reason: string) {
		return withLoading(async () => {
			const data = await overtimeAPI.reject(id, reason)
			const index = requests.value.findIndex((req) => req.id === id)
			if (index !== -1) {
				requests.value[index] = data
			}
			clearCache()
			return data
		}, 'Failed to reject request')
	}

	async function cancelRequest(id: number) {
		return withLoading(async () => {
			const data = await overtimeAPI.cancel(id)
			const index = requests.value.findIndex((req) => req.id === id)
			if (index !== -1) {
				requests.value[index] = data
			}
			clearCache()
			return data
		}, 'Failed to cancel request')
	}

	/**
	 * Bulk update status for multiple requests - much faster than individual updates
	 */
	async function bulkUpdateStatus(ids: number[], status: 'approved' | 'rejected' | 'pending') {
		return withLoading(async () => {
			const result = await overtimeAPI.bulkUpdateStatus(ids, status)
			// Update local state for all affected requests
			ids.forEach((id) => {
				const index = requests.value.findIndex((req) => req.id === id)
				if (index !== -1 && requests.value[index]) {
					requests.value[index]!.status = status
				}
			})
			clearCache()
			return result
		}, 'Failed to bulk update status')
	}

	function clearCache() {
		lastFetch.value = null
	}

	function reset() {
		requests.value = []
		currentRequest.value = null
		_loadingCount.value = 0
		error.value = null
		lastFetch.value = null
		paginationMeta.value = { count: 0, next: null, previous: null }
	}

	/** Fetch server-side aggregated employee statistics */
	async function fetchEmployeeStats(params?: {
		start_date?: string
		end_date?: string
		status?: string
		employee?: number
	}) {
		return overtimeAPI.employeeStats(params)
	}

	/** Fetch server-side aggregated project statistics */
	async function fetchProjectStats(params?: {
		start_date?: string
		end_date?: string
		status?: string
		project?: number
	}) {
		return overtimeAPI.projectStats(params)
	}

	/** Fetch server-side summary statistics (with optional previous period) */
	async function fetchSummaryStats(params?: {
		start_date?: string
		end_date?: string
		prev_start_date?: string
		prev_end_date?: string
	}) {
		return overtimeAPI.summaryStats(params)
	}

	return {
		// State
		requests,
		currentRequest,
		loading,
		error,
		paginationMeta,

		// Computed
		pendingRequests,
		approvedRequests,
		rejectedRequests,
		getRequestById,
		getRequestsByEmployee,
		getRequestsByProject,

		// Actions
		fetchRequests,
		fetchRequestById,
		createRequest,
		updateRequest,
		deleteRequest,
		approveRequest,
		rejectRequest,
		cancelRequest,
		bulkUpdateStatus,
		clearCache,
		reset,
		fetchAllRequests,
		fetchEmployeeStats,
		fetchProjectStats,
		fetchSummaryStats,
	}
})
